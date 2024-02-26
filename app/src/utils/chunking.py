import tiktoken
from typing import List, Optional   

tokenizer = tiktoken.get_encoding('cl100k_base')

def chunking(text: str, 
             chunk_size: int=350, 
             max_num_chunks: int=100,
             min_chunk_char: int = 25
             ) -> List[str]:

    """
    Takes in a text and returns a list of chunks
    #TODO: add more scenarios for punctuation, e.g. PDF shouldn't have '\n' as natural stop 
    #TODO: include overlappting text between chunks. https://python.langchain.com/docs/modules/data_connection/document_transformers/text_splitters/recursive_text_splitter
    """
    if not text or text.isspace():
        return

    # Tokenize the text
    tokens = tokenizer.encode(text, disallowed_special=())

    chunks = []

    num_chunks = 0

    while tokens and num_chunks < max_num_chunks:
        # Get the first chunking_size tokens
        chunk = tokens[:chunk_size]

        # Decode the chunk
        chunk_text = tokenizer.decode(chunk)

        # Skip the chunk if it is empty or shitespace
        if not chunk_text or chunk_text.isspace() or len(chunk_text) < min_chunk_char:
                
            # Remove tokens corresponding to teh chunk text from the remaining tokens
            tokens = tokens[len(chunk):]

            continue
        
        # Find the last period or puctuation mark in the chunk
        last_period =max(chunk_text.rfind("."),
                chunk_text.rfind("?"),
                chunk_text.rfind("!"),
                chunk_text.rfind("\n"),
            )
        
        # If there is a valud punctuation mark, split the chunk there
        if last_period != -1 and last_period >= min_chunk_char:
            chunk_text = chunk_text[: last_period + 1]

        # Remove newline chars and strip any leading or trailing whitespze
        chunk_text_to_apend = chunk_text.replace("\n", " ").strip()

        chunks.append(chunk_text_to_apend)

        # Remove tokens corresponding to the chunk text from the remaining tokens
        tokens = tokens[len(tokenizer.encode(chunk_text, disallowed_special=())):]
        
        # Increment the number of chunks
        num_chunks += 1

    return chunks