from openai import OpenAI
import os
import time
from loguru import logger

level_assistant = logger.level("ASSISTANT", no=15, color="<green>", icon="♣")


client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

class Assistant:

    def __init__(self, assistant_name: str, prompt: str):
        self.model_base = 'gpt-3.5-turbo-1106'
        self.model_advanced = 'gpt-4-1106-preview'
        self.model_used = self.model_base
        self.name = assistant_name

        assistant = client.beta.assistants.create(
            name = self.name,
            instructions = prompt,
            model = self.model_used
        )
        
        thread = client.beta.threads.create()
        self.thread_id = thread.id
        self.assistant_id = assistant.id
        self.messages = []


    def create_assistant(self):
        """
        Instantiate an assistant, and return assistant_id and thread_id
        """
        



    def run_query(self, message: str) -> str:
        """
        Run a query and return the response
        """

        message = client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user",
            content=message
        )
        self.messages.append({"role": message.role, "content": message.content[0].text.value})
        
        run = client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
        )

        run = self.wait_for_run_completion(run.id)

        response = self.get_last_message()
        self.messages.append(response)

        return response['content']
    


    def wait_for_run_completion(self, run_id):
        """
        Check for run status every second until it is completed
        """
        while True:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=self.thread_id, run_id=run_id)
            if run.status in ['completed', 'failed', 'requires_action']:
                return run
            

    def get_last_message(self):
        """
        Get the last messagae
        """
        thread_messages = client.beta.threads.messages.list(self.thread_id)
        data = thread_messages.data[0]
        logger.opt(lazy=True).log("ASSISTANT", f"Message: {thread_messages.data[1]} | Response: {data}")
        return {"role": data.role, "content": data.content[0].text.value}
    
    

    def get_all_messages(self):
        """
        Get all messages in the thread
        """
        thread_messages = client.beta.threads.messages.list(self.thread_id)
        messages = []
        for msg in thread_messages:
            messages.append({"role": msg.role, "content": msg.content[0].text.value})
        return messages

