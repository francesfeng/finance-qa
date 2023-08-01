import asyncio
from src.connect.datastore import DataStore
from src.connect.db import Database
from src.connect.gpt import get_chat_completion_stream, get_chat_completion

from src.models.models import Query, PromptType
from src.models.prompt import get_prompt

import timeit
from loguru import logger
logger.add("file_prompt.log", rotation="12:00")  
level_datastore = logger.level("RETRIEVAL", no=38, color="<yellow>", icon="♣")
level_text = logger.level("TEXT", no=30, color="<green>", icon="♨")
level_sql = logger.level("SQL", no=30, color="<green>", icon="♨")



class Agent:

    def __init__(self):
        """
        Initialise the agent.
        """
        self.datastore = DataStore()
        self.db = Database()


    async def query_text_table(self, query: Query, model: PromptType):
        
        # Retrieve context, and record the start and end time to calculate processing time
        time_start_datastore = timeit.default_timer()
        res_datastore = await self.datastore.query(query)
        time_end_datastore = timeit.default_timer()
        time_datastore = time_end_datastore - time_start_datastore

        logger.opt(lazy=True).log("RETRIEVAL", f"Query: {query.query} | Processing Time: {time_datastore} | Response: {[i.dict() for i in res_datastore]}")

        # Reformat the context
        text, source = self.datastore.format_response(res_datastore)

        # Retrieve the prompt template and filled with query and context
        if model == PromptType.table_datastore:
            messages = get_prompt('table_datastore', query.query, text)
        elif model == PromptType.text:
            messages = get_prompt('text', query.query, text)
        else:
            raise ValueError(f"Model {model} not recognised")

        # Call ChatGPT to generate the answer in streaming text
        return get_chat_completion_stream(messages)
    

    
    async def query_non_stream(self, query: Query, model: PromptType):
        
        # Retrieve context, and record the start and end time to calculate processing time
        time_start_datastore = timeit.default_timer()
        res_datastore = await self.datastore.query(query)
        time_end_datastore = timeit.default_timer()
        time_datastore = time_end_datastore - time_start_datastore

        logger.opt(lazy=True).log("RETRIEVAL", f"Query: {query.query} | Processing Time: {time_datastore} | Response: {[i.dict() for i in res_datastore]}")

        # Reformat the context
        text, source = self.datastore.format_response(res_datastore)

        # Retrieve the prompt template and filled with query and context
        if model == PromptType.table_datastore:
            messages = get_prompt('table_datastore', query.query, text)
        elif model == PromptType.text:
            messages = get_prompt('text', query.query, text)
        else:
            raise ValueError(f"Model {model} not recognised")

        # Call ChatGPT to generate the answer in streaming text
        return get_chat_completion(messages)
    


    async def query_sql(self, query: str):
        # Retrieve full schema from database
        schemas = self.db.get_schemas()

        messages = get_prompt('sql', query, schemas)
        
        time_start_sql = timeit.default_timer()
        res =  get_chat_completion(messages)
        time_end_sql = timeit.default_timer()

        time_sql = time_end_sql - time_start_sql
        logger.opt(lazy=True).log("SQL", f"Query: {query} | Processing Time: {time_sql} | Response: {res}")

        sql = res.replace("SQL:", "").strip().replace("\n", " ") 
        data = self.db.execute_query(sql)
        return data
