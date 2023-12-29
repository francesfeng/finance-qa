import asyncio
import yaml
from typing import List, Optional
from loguru import logger
import json
import time
logger_sqlagent = logger.level("SQL_AGENT", no=38, color="<green>", icon="♣")

from .prompt import get_prompt
from app.src.connect.db import Database
from app.src.connect.gpt_v2 import get_chat_completion_v2, get_chat_completion_json


class SQLAgent:
    
    def __init__(self, query: str):
        self.query = query
        self.tables = set()  
        self.model_basic = "gpt-3.5-turbo-1106"
        self.model_advanced = "gpt-4-1106-preview"
        self.schema_use = []
        self.source_use = ''


        with open('app/src/connect/schemas.yaml', 'r') as file:
            # Load the content using yaml.load
            data = yaml.load(file, Loader=yaml.FullLoader)
            self.schema = data['schema']
            self.schema_short = data['schema_short']

        with open('app/src/connect/source.yaml', 'r') as file:
            self.source = yaml.load(file, Loader=yaml.FullLoader)

        self.messages_tables = get_prompt('sql_table', self.query, self.schema_short)
        self.messages_sql = []

    
    async def get_tables(self, msg: Optional[str] = None, attempt: int = 0):
        """
        Get the tables from the query

        Args:
            msg: Error messages from previous runs of SQL generation, likely due to missing tables/data fields
            attempt: The number of attempt to retrieve tables

        Returns:
            status: 'process' -> progress to generate SQL step
            message: None -> no error message
        """
        # Generate messages that used to retrieve tables
        if msg:
            new_msg = msg.replace('schema','table') + '. Please try again. Think step by step.'
            self.messages_tables.append({"role": "assistant", "content": ', '.join(self.tables)})
            self.messages_tables.append({"role": "user", "content": new_msg})

        # Get the tables
        res = get_chat_completion_v2(self.messages_tables, temperature=0, model=self.model_advanced, max_tokens=100)
        # Convert to table list

        # Alaways adding new tables, not removing
        for t in res.split(','):
            self.tables.add(t.strip())

        # Get the source and schema used relating to the tables used
        self.source_use = self.get_sources_from_tables(self.tables)
        self.schema_use = self.get_schema_from_tables(self.tables)

        # For the first attempt, use the default error state
        if attempt == 0:
            self.messages_sql = get_prompt('sql', self.query, '\n\n'.join(self.schema_use))

        # For the second attempt, remove the default error state from prompt
        else:
            self.messages_sql = get_prompt('sql_without_error', self.query, '\n\n'.join(self.schema_use))

        return {'status': 'process', 'message': None}
    

    async def get_data(self):
        """
        Get the data from the query

        Returns:
            res: The result of the SQL generation, which contains:
                - status: 
                    'success' -> successfully generated SQL, 
                    'pending' -> pending to generate SQL, 
                    'fail, error or anything else' -> regenerate SQL
                - message: None -> this fields only used when there is error in generating SQL
                - sql: The generated SQL
                - data: The data retrieved from the SQL
                - explanation: The explanation of the SQL
        """
        res = {'status': 'pending', 'message': None}
        count = 0 # Count the number of SQL generated
        count_table = 0  # Count the number of tables generated

        while True:
            
            # Max attempt to generate SQL is 3 times
            if count == 3:
                break

            if res['status'] == 'pending':

                # Get the table names, update schema and messages used to generate SQL
                res = await self.get_tables(res["message"], count_table) 
                count_table += 1
                logger.opt(lazy=True).log("SQL_AGENT", f"Get Tables | Attempt: {count_table} | Query: {self.query} | Tables: {self.tables}")

            elif res['status'] == 'success' and 'sql' in res and res['sql'] is not None:

                # Run the SQL
                sql = res['sql'].strip().replace("\n", " ")
                data = await self.run_sql(sql)

                # If the SQL is successfully executed, return the result
                if not data.startswith('Error'):
                    res['sql'] = sql
                    res['data'] = data
                    res['source'] = self.source_use
                    logger.opt(lazy=True).log("SQL_AGENT", f"Success generate SQL | Attempt: {count} | Response: {res} | Tables: {self.tables} | Query: {self.query}")
                    return res
                
                # If errors in executing SQL, append the error message and try again
                else:
                    error_msg = ' '.join([l.strip() for l in data.split('\n')])
                    res['message'] = error_msg
                    msg_assistant = json.dumps({"role": "assistant", "content": {"status": "success", "sql": res['sql']}})
                    self.messages_sql.append(msg_assistant)
                    logger.opt(lazy=True).log("SQL_AGENT", f"Error in executing SQL | Attempt: {count + 1} | Query: {self.query} | Error: {res} | Tables: {self.tables} | Query: {self.query}")
                    
                    # Update the status to process and try again
                    res = {'status': 'process', 'message': None}

            else:

                # When there is error message, because error in executing SQL, append the error message and try again
                if res['message']:
                    self.messages_sql.append({"role": "assistant", "content": res['message']})
                    self.messages_sql.append({"role": "user", "content": 'Make an assumption. Please try again. Think step by step.'})
                
                # When new table names are generated, update the schema and messages (remove default error state), and try again
                res = get_chat_completion_json(self.messages_sql, model=self.model_advanced, max_tokens=600)
                logger.opt(lazy=True).log("SQL_AGENT", f"Process to generate SQL | Attempt: {count + 1} | Response: {res} | Tables: {self.tables} | Query: {self.query}")
                count += 1
            

        return {'status': 'failed', 'message': 'Reached max number of attempts.'}
    

    async def get_sql(self, tables: List[str]):
        schema = self.get_schema_from_tables(tables)

        messages = get_prompt('sql', self.query, '\n\n'.join(schema))

        res = get_chat_completion_json(messages, model=self.model_advanced, max_tokens=600)

        return res



    def get_schema_from_tables(self, tables: List[str]) -> List[str]:
        """
        Get a list of schemas from a list of tables
        """
        # produce valid schemas that for the tables required only          ]
        schemas_table = self.schema.split('\n')
        valid_schemas = [schemas_table[0]]+[i for i in schemas_table if i.split(',')[0] in tables] 
        # Retrieve full scheme if no valid table names are provided
        if len(valid_schemas) == 0:
            valid_schemas = self.schema
            logger.warning(f"Error: No schema found on these tables {tables}, import all schemas to the prompt")
        
        return valid_schemas
    

    def get_sources_from_tables(self, tables: List[str]) -> str:
        # Retrieve data source by table names
        sources = set()
        for t in tables:
            # get table name if exists in schema
            tb = self.source.get(t)

            # get table source if table exists
            if tb:
                source = tb.get('source')

                # add source to the set if source exists
                if source:
                    sources.add(source)

        # if no source found, use default source    
        if len(sources) == 0:
            source_list = 'Endepth Data Insight'
        else:
            source_list = ', '.join(sources)
        return source_list
    

    async def run_sql(self, query: str):
        db = Database()
        time_start = time.time()
        data = db.execute_query(query)
        time_end = time.time()
        #logger.opt(lazy=True).log("RUNSQL", f"Query: {query} | Processing Time: {stop - start} | Response: {data}")
        return data

    