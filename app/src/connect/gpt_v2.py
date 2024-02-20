from typing import List, Dict, Optional
from openai import OpenAI, AsyncOpenAI
import os
import json
from loguru import logger

level_gpt = logger.level("GPT", no=38, color="<yellow>", icon="♣")

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
async_client = AsyncOpenAI(api_key=os.environ['OPENAI_API_KEY'])

def get_chat_completion_json(
        messages, 
        model="gpt-3.5-turbo-1106", 
        temperature: float = 0, 
        max_tokens: int = None,
        ):

    """
    Get the chat completion using OpenAI's Chat Completion API.
    Adding json output compared to v1
    """
    if max_tokens:
        response = client.chat.completions.create(
            model=model,
            response_format={ "type": "json_object" },
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
    else:
        response = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object" },
            messages=messages,
            temperature=temperature,
        ) 

    logger.opt(lazy=True).log("GPT", f"Chat Completion JSON| Message: {json.dumps(messages)} | Response: {response}")

    choices = response.choices
    finish_reason = choices[0].finish_reason

    if finish_reason == "length":
        completion = {'Error': 'Max tokens exceeded.'}
    elif finish_reason == "stop":
        completion = choices[0].message.content.strip()
        completion = json.loads(completion)
    else:
        error_msg = choices[0].message.content.strip()
        completion = json.loads(error_msg)
    return completion


def get_chat_completion_v2(
        messages, 
        model="gpt-3.5-turbo-1106", 
        temperature: float = 0, 
        max_tokens: int = None,
        ):
    
    if max_tokens:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

    else:   
        response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            ) 
    
    logger.opt(lazy=True).log("GPT", f"Chat Completion | Message: {json.dumps(messages)} | Response: {response}")

    choices = response.choices
    finish_reason = choices[0].finish_reason

    if finish_reason == "length":
        logger.error(f"GPT Chat Completion | Max tokens exceeded | Message: {json.dumps(messages)}")
        return
    elif finish_reason == "stop":
        completion = choices[0].message.content.strip()
        return completion
    else:
        logger.error(f"GPT Chat Completion | Stop Reason: {finish_reason} | Message: {json.dumps(messages)}")
        return

def get_chat_completion_stream_v2(messages, model="gpt-3.5-turbo-1106", temperature=0):
    """
    Get the chat completion using OpenAI's Chat Completion API.
    Returning JSON output, transformed into 
    """
    for response in client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        stream=True
    ):
        
        #yield response.choices[0].delta.content
         
        data = {"finish_reason": response.choices[0].finish_reason, "content": response.choices[0].delta.content}
        sse_data = f"data: {json.dumps(data)}\n\n"
        yield sse_data

        if response.choices[0].finish_reason == 'stop':
            return


def get_function_call(messages, tools, model = "gpt-4-1106-preview", temperature: float = 1):
    """
    Return function alls

    Args:
        messages: List of messages
        tools: List of function specifications
        model: Defaults to "gpt-3.5-turbo".
        temperature: Defaults to 0.
    
    Returns:
        List of function calls: {function_name: {arg1: value1, arg2: value2}}
    """

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        tools = tools
    )
    logger.opt(lazy=True).log("GPT", f"Function Call | Message: {json.dumps(messages)} | Response: {response}")


    tool_calls = response.choices[0].message.tool_calls
    functions = {}
    if tool_calls:
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            functions[function_name] = function_args

        
        return functions
    else:
        return


def get_embeddings_v2(texts: List[str], model: str = 'text-embedding-3-small') -> List[List[float]]:
    """
    Get the embeddings of a list of texts
    """
    response = client.embeddings.create(
        input=texts,
        model=model
    )

    data = response.data

    return [result.embedding for result in data]


async def get_image(file_id: str):
    """
    Get the image from OpenAI's file API
    """
    image_data = await async_client.files.content(file_id)
    return image_data.read()



