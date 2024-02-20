"""
    Manage the thread, a thread is a list of messages with a specific assistant, 
    Each thread is a new topic, and each message is a new question or response that is to ask follow-up questions.
    Multiple threads is a report 
"""

from openai import OpenAI
import time
import os
from loguru import logger
from typing import List, Dict, Optional, Any
from app.src.runner.function_call import execute_sql

level_assistant = logger.level("ASSISTANT", no=15, color="<green>", icon="♣")


from app.src.config.prompt.assistant_prompts import get_assistant_prompt
from app.src.config.config import Config
from app.models.models import AssistantModel


client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])


def create_assistant(assistant_name: str, 
                     model: str = 'gpt-3.5-turbo', 
                     code_interpreter: bool = False, 
                     file_obj: Optional[Any] = None
                     ) -> AssistantModel:
    """
    Instantiate an assistant, and return assistant_id and thread_id
    """
    
    # get assistant prompt
    assistant_prompt = get_assistant_prompt(assistant_name)

    
    if code_interpreter:
         assistant = client.beta.assistants.create(
            name = assistant_name,
            instructions = assistant_prompt,
            model = model,
            tools = [{"type": "code_interpreter"}],
            file_ids = [file_obj.id]
        )
    else:
        assistant = client.beta.assistants.create(
        name = assistant_name,
        instructions = assistant_prompt,
        model = model
    )
        
    thread = client.beta.threads.create()

    
    return AssistantModel(assistant_id=assistant.id, thread_id=thread.id)



def submit_query(assistant_id: str, 
                 thread_id: str, 
                 query: str, 
                 use_code_interpreter: bool=False
                 ) -> List[Dict[str, str]]:
    """
    Add new message to a thread, run the thread and return the response
    
    """

    message = add_message_to_thread(thread_id, "user", query)

    # Create a run
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )

    # Wait for the run to complete
    run = wait_for_run_completion(thread_id, run.id)
    print(f"Run ID is {run.id}")

    # Get the last message, the assistant's response

    # If not using code interpreter, get the assistant's response
    if use_code_interpreter == False:
        messages_dict = get_assistant_response(thread_id)
        messages = [{**v, "run_id": run.id} for k, v in messages_dict.items()]

        # Reverse the messages, so that the latest message is at the end
        messages = messages[::-1]

    # If using code interpreter, get the assistanats' response and code interpreter's input and output
    else:
        messages_lst = get_assistant_response_with_code_interpreter(thread_id, run.id)
        messages = [{**v, "run_id": run.id} for v in messages_lst]

    logger.opt(lazy=True).log("ASSISTANT", f"Query: {query} | Response: {messages}")

    return messages



def add_message_to_thread(thread_id: str, role: str, content: str, file_id: Optional[str] = None):
    """
    Add new message to a thread
    """
    if not file_id:
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=content
        )
    else:
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=content,
            file_ids=[file_id]
        )
    return message


def upload_file(file_path: str):
    file = client.files.create(
        file=open(file_path, 'rb'),
        purpose = 'assistants'
        )
    return file
    

def wait_for_run_completion(thread_id: str, run_id: str):
    """
    Check for run status every second until it is completed
    """
    while True:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        if run.status in ['completed', 'failed', 'requires_action']:
            return run
        

def get_assistant_response(thread_id: str) -> Dict[str, Dict[str, str]]:
    """
        Retrieve all the messages reponded by the assistant.

        Return a dictionary of messages, with the key as the message id

    """   
    thread_messages = client.beta.threads.messages.list(thread_id).data 
    messages = {}
    for m in thread_messages:
        if m.role != 'assistant':
            break 
        image_files = []
        content = ''
        for c in m.content:       
            if c.type == 'text':
                content += c.text.value
            elif c.type == 'image_file':
                image_files.append(c.image_file.file_id)
            else:
                print(f"Unknown content type: {c.type}")
            msg = {"role": "assistant", 
                            "content": content, 
                            "created_at": m.created_at
                            }
        if len(image_files) > 0:
            # Add image files to the message dictionary
            msg["image_files"] = image_files

            # # Download image files to local temp folder
            # for file_id in image_files:
            #     download_image_file(file_id)

        messages[m.id] = msg

                
    return messages   


#TODO: delete, replaced by saving to database
def download_image_file(file_id: str):
    """
    Download image file to local temp folder
    
    :param file_id: The OpenAI's file ID of the image file to be downloaded
    
    file saved as temp/{file_id}.png
    """
    image_data = client.files.content(file_id)
    image_data_bypes = image_data.read()

    file_name = f"temp/{file_id}.png"

    with open(file_name, 'wb') as f:
        f.write(image_data_bypes)

    return


    
def get_assistant_response_with_code_interpreter(thread_id: str, run_id: str):
    """
    Get the code interpreter's intput and output from a thread + run
    """

    asst_response = get_assistant_response(thread_id)
    run_steps = client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run_id)

    
    all_messages = []
    for m in run_steps.data:

        # If the step is a message creation, get the message id and get the message details from thread messages
        if m.step_details.type == 'message_creation':

            # get message_id
            message_id = m.step_details.message_creation.message_id

            # get message details
            all_messages.append(asst_response[message_id]) 
            
        if m.step_details.type == 'tool_calls':
            for code in m.step_details.tool_calls:
                code_interpreter = code.code_interpreter

                # get the input
                input = code_interpreter.input

                # get all outputs
                logs = []
                image_files = []
                code_dict = {}
                code_dict["input"] = input
                for output in code_interpreter.outputs:

                    # get the logs list from output if any
                    if output.type == 'logs':
                        logs.append(output.logs)
                    
                    # get the image files list from output if any
                    elif output.type == 'image':
                        image_files.append(output.image.file_id)

                # construct code dictionary
                if len(logs) > 0:
                    code_dict["output_logs"] = logs

                if len(image_files) > 0:
                    code_dict["output_image_files"] = image_files

                all_messages.append({"role": "code_interpreter", 
                                     "code": code_dict,
                                     "created_at": m.created_at
                                     })
    # Reverse the messages, so that the latest message is at the end
    return all_messages[::-1]


def get_all_messages(thread_id: str):
    """
    Get all messages from a thread
    
    :param thread_id: The ID of the thread
    :type thread_id: str
    :return: A list of messages from the thread
    :rtype: list
    """
    thread_messages = client.beta.threads.messages.list(thread_id)
    messages = []
    for msg in thread_messages:
        messages.append({"role": msg.role, "content": msg.content[0].text.value})
    return messages


    
