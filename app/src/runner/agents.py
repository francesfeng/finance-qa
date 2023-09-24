import asyncio
import json
from typing import Optional
from app.src.connect.datastore import DataStore
from app.src.connect.db import Database
from app.src.connect.gpt import get_chat_completion_stream, get_chat_completion

from app.models.models import Query, Type
from app.src.runner.prompt import get_prompt


import timeit
import yaml
#from loguru import logger
#logger.add("file_prompt.log", rotation="12:00")  
#level_classification = logger.level("CLASSIFICATION", no=38, color="<yellow>", icon="♣")
#level_related = logger.level("RELATED", no=38, color="<yellow>", icon="♣")
#level_datastore = logger.level("RETRIEVAL", no=38, color="<yellow>", icon="♣")
#level_text = logger.level("TEXT", no=30, color="<green>", icon="♨")
#level_table= logger.level("TABLE", no=30, color="<magenta>", icon="♨")
#level_table_chart = logger.level("TABLECHART", no=30, color="<blue>", icon="♨")
#level_sql = logger.level("SQL", no=30, color="<green>", icon="♨")
#level_run_sql = logger.level("RUNSQL", no=30, color="<green>", icon="♨")
#level_sql_chart = logger.level("SQLECHART", no=30, color="<green>", icon="♨")
#level_data_text = logger.level("DATATEXT", no=30, color="<green>", icon="♨")



class Agent:

    def __init__(self):
        """
        Initialise the agent.
        """
        self.datastore = DataStore()
        

        with open('app/src/connect/schemas.yaml', 'r') as file:
            # Load the content using yaml.load
            data = yaml.load(file, Loader=yaml.FullLoader)
            self.schema = data['schema']
            self.schema_short = data['schema_short']



    async def classification_related(self, query: str):
        schema_short = self.schema_short
        messages = get_prompt('classification_and_related', query, schema_short)

        response = get_chat_completion(messages)
        return json.loads(response)
    

    async def classification(self, query: str):
        schema_short = self.schema_short
        messages = get_prompt('classification', query, schema_short)
        start = timeit.default_timer()
        res = get_chat_completion(messages)
        end = timeit.default_timer()

        #logger.opt(lazy=True).log("CLASSIFICATION", f"Query: {query} | Processing Time: {end - start} | Response: {res}")

        return res
    

    async def related(self, query: str):
        schema_short = self.schema_short
        messages = get_prompt('related', query, schema_short)

        start = timeit.default_timer()
        res = get_chat_completion(messages)
        end = timeit.default_timer()

        #logger.opt(lazy=True).log("CLASSIFICATION", f"Query: {query} | Processing Time: {end - start} | Response: {res}")

        return res



    async def query_text_table(self, query: str, is_streaming: bool = False):
        
        # Contruct Query class
        query_class = Query(query = query, filter = {"type": Type.table}, top_k = 5)

        # Retrieve context, and record the start and end time to calculate processing time
        retrieved = await self._retrieval(query_class)
        # Reformat the context
        text, source = self.datastore.format_response(retrieved)

        # Terminate the process, when none of retrieved text has relevant score > 0.8
        if len(text) == 0:
            return 'Sorry, seems the question is not relevant. Could you please ask a different question?'

        # Retrieve the prompt template and filled with query and context
        messages = get_prompt('table_datastore', query_class.query, text)
        
        if is_streaming:
            # Call ChatGPT to generate the answer in streaming text
            return get_chat_completion_stream(messages)
        else:
            # Call ChatGPT to generate the answer in non-streaming text
            time_start_table = timeit.default_timer()
            res = get_chat_completion(messages, temperature=1)
            time_end_table = timeit.default_timer()
            #logger.opt(lazy=True).log("TABLE", f"Query: {query_class} | Processing Time: {time_end_table - time_start_table} | Response: {res}")
            return res



    async def query_table_to_chart(self, query: str, data: str) -> Optional[str]:

        # Retrieve context, and record the start and end time to calculate processing time
        time_start_chart = timeit.default_timer()
        messages = get_prompt('table_to_chart', context = data)
        res = get_chat_completion(messages)
        time_end_chart= timeit.default_timer()

        res = "{" + res + "}"

        #logger.opt(lazy=True).log("TABLECHART", f"Query: {query} | Processing Time: {time_end_chart - time_start_chart} | Response: {res}")

        return self._check_json(res)

        

    async def query_text(self, query: str, is_streaming: bool = False):
        query_class = Query(query=query, top_k=10)
        
        # Retrieve context, and record the start and end time to calculate processing time
        retrieved = await self._retrieval(query_class)
        
        # Reformat the context
        text, source = self.datastore.format_response(retrieved)
        # Terminate the process, when none of retrieved text has relevant score > 0.8
        if len(text) == 0:
            return 'Sorry, seems the question is not relevant. Could you please ask a different question?'

        # Retrieve the prompt
        messages = get_prompt('text', query_class.query, text)

        # Get streaming result
        if is_streaming:
            return get_chat_completion_stream(messages)
        
        # Get non-streaming result
        else:
            time_start_text = timeit.default_timer()
            res = get_chat_completion(messages, temperature=1)
            time_end_text = timeit.default_timer()
            #logger.opt(lazy=True).log("TEXT", f"Query: {query_class.query} | Processing Time: {time_end_text - time_start_text} | Response: {res}")
            return res
    



    async def query_combined(self, query: str, is_streaming: bool = True):
        """
            Retrieved context include both Text and Table
            Output has 2 parts: Table and Text
        """

        query_text = Query(query = query, top_k = 10)
        retrieved_text = await self._retrieval(query_text)
        text, source = self.datastore.format_response(retrieved_text)

        messages = get_prompt('combined', query, text)

        # Get streaming result
        if is_streaming:
            return get_chat_completion_stream(messages)
        
        # Get non-streaming result
        else:
            time_start_text = timeit.default_timer()
            res = get_chat_completion(messages)
            time_end_text = timeit.default_timer()
            #logger.opt(lazy=True).log("TEXT", f"Query: {query} | Processing Time: {time_end_text - time_start_text} | Response: {res}")
            return res


    async def classify_text(self, query: str):
        """
            From retrieved text, classify whether it is text table, or error
            
            Error: if none of retrieved text has relevant score > 0.8
            Table: if there is at least 1 table in retrieved text
            Text: if there is no table in retrieved text

        """
        query_class = Query(query=query, top_k=10)
        retrieved_text = await self._retrieval(query_class)

        types = [r.metadata.type for r in retrieved_text if r.score > 0.8]
        num_table = sum([True if t == 'table' else False for t in types])

        if len(types) == 0:
            return 'error'
        elif num_table > 0:
            return 'table'
        else:
            return 'text'
        

    
    # async def query_non_stream(self, query: Query, model: str):
        
    #     # Retrieve context, and record the start and end time to calculate processing time
    #     retrieved = await self._retrieval(query)
    #     # Reformat the context
    #     text, source = self.datastore.format_response(retrieved)

    #     # Retrieve the prompt template and filled with query and context
    #     if model == PromptType.table_datastore:
    #         messages = get_prompt('table_datastore', query.query, text)
    #     elif model == PromptType.text:
    #         messages = get_prompt('text', query.query, text)
    #     else:
    #         raise ValueError(f"Model {model} not recognised")

    #     # Call ChatGPT to generate the answer in streaming text
    #     return get_chat_completion(messages)
    


    async def query_sql(self, query: str):

        # Retrieve full schema from database, and construct prompt
        schema = self.schema
        messages = get_prompt('sql', query, schema)
        
        # Call ChatGPT to generate SQL
        time_start_sql = timeit.default_timer()
        res =  get_chat_completion(messages, max_tokens=350)
        time_end_sql = timeit.default_timer()

        time_sql = time_end_sql - time_start_sql
        #logger.opt(lazy=True).log("SQL", f"Query: {query} | Processing Time: {time_sql} | Response: {res}")

        # Reformat SQL Code
        sql = res.replace("SQL:", "").strip().replace("\n", " ") 
        return sql
    

    # TODO: Move to query_sql
    async def run_sql(self, query: str):
        db = Database()
        start = timeit.default_timer()
        data = db.execute_query(query)
        stop = timeit.default_timer()
        #logger.opt(lazy=True).log("RUNSQL", f"Query: {query} | Processing Time: {stop - start} | Response: {data}")
        return data
    

    async def query_sql_chart(self, query: str, data: str) -> Optional[str]:
        # From data to generate chart code
        time_start_chart = timeit.default_timer()
        messages = get_prompt('sql_to_chart', query, data)
        res = get_chat_completion(messages)
        time_end_chart = timeit.default_timer()

        res = "{" + res + "}"
        #logger.opt(lazy=True).log("SQLECHART", f"Query: {query} | Processing Time: {time_end_chart - time_start_chart} | Response: {res}")

        return self._check_json(res)
    

    async def query_sql_table(self, query: str) -> str:
        sql = await self.query_sql(query)
        try: 
            return await self.run_sql(sql)
        except Exception as e:
            #logger.error(f"Query: {query} | SQL: {sql} | Error: {e}")
            return 'Error in SQL query'
        
    
    async def query_data_to_text(self, query: str, data: str) -> str:
        messages = get_prompt('data_to_text', query, data)
        start = timeit.default_timer()
        res = get_chat_completion(messages)
        end = timeit.default_timer()
        #logger.opt(lazy=True).log("DATATEXT", f"Query: {query} | Processing Time: {end - start} | Response: {res}")
        return res
        
    

    def _check_json(self, json_str: str) -> Optional[str]:
        """
        Check if the json string is valid
        When there is "Extra data" error, remove the last character and try again
        If still not valid, return None
        """
         
        valid_str = json_str
        try:
            json.loads(valid_str)
        except Exception as e:

            # Remove the last character and try again
            if e.__dict__["msg"] == "Extra data":
                valid_str = valid_str[:-1]
                try: 
                    json.loads(valid_str)
                except Exception as e:
                    valid_str = None
            else:
                valid_str = None

        return valid_str
    

    async def _retrieval(self, query: Query):

        start = timeit.default_timer()
        res = await self.datastore.query(query)
        stop = timeit.default_timer()
        #logger.opt(lazy=True).log("RETRIEVAL", f"Query: {query} | Processing Time: {stop - start} | Response: {[i.dict() for i in res]}")

        return res