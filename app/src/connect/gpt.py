from typing import List
import openai
import os
import timeit

from tenacity import retry, wait_random_exponential, stop_after_attempt
from loguru import logger
logger.add("file_prompt.log", rotation="12:00")  
level_gpt = logger.level("GPT", no=38, color="<yellow>", icon="♣")

openai.api_key = os.getenv("OPENAI_API_KEY")

@retry(wait=wait_random_exponential(multiplier=1, max=20), stop=stop_after_attempt(3))
def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Embed texts using OpenAI's ada model.

    Args:
        texts: The list of texts to embed.

    Returns:
        A list of embeddings, each of which is a list of floats.

    Raises:
        Exception: If the OpenAI API call fails.
    """
    # Call the OpenAI API to embed the texts
    response = openai.Embedding.create(input=texts, model="text-embedding-ada-002")

    # Extract the embeddings from the response
    data = response["data"]

    # Return the embeddings as a list of lists of floats
    return [result["embedding"] for result in data]


@retry(wait=wait_random_exponential(multiplier=1, max=20), stop=stop_after_attempt(3))
def get_chat_completion_stream(messages, model="gpt-3.5-turbo", temperature=0):
    """
    Get the chat completion using OpenAI's Chat Completion API.
    Using streaming output
    """
    for response in openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        stream=True
    ):
        if response['choices'][0]['finish_reason'] == 'stop':
            break
        yield response['choices'][0]['delta']['content']


@retry(wait=wait_random_exponential(multiplier=1, max=20), stop=stop_after_attempt(3))
def get_chat_completion(messages, model="gpt-3.5-turbo", temperature: float = 0, max_tokens: int = None):

    """
    Get the chat completion using OpenAI's Chat Completion API.
    """
    start = timeit.default_timer()
    if max_tokens:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
    else:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
        ) 
    stop = timeit.default_timer()
    logger.opt(lazy=True).log("GPT", f"Query: {messages} | Processing Time: {stop - start} | Response: {response}")

    choices = response["choices"]
    finish_reason = choices[0]["finish_reason"]

    if finish_reason == "length":
        completion = 'ERROR: Max tokens exceeded.'
    else:
        completion = choices[0].message.content.strip()
    return completion



@retry(wait=wait_random_exponential(multiplier=1, max=20), stop=stop_after_attempt(3))
def get_function_call(messages, functions, function_call = None, model = "gpt-3.5-turbo"):
    return


def test_query(num: int):
    messages = [
        {'role': 'user', 'content': f"Count to {num}, with a comma between each number and no newlines. E.g., 1, 2, 3, ..."}
    ]

    for response in openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=messages,
        temperature=0,
        stream=True
    ):
        if response['choices'][0]['finish_reason'] == 'stop':
            break
        yield response['choices'][0]['delta']['content']
