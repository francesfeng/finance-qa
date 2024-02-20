import asyncio
import json
from functools import partial
import asyncio
import time

from typing import Optional, List, Dict
from app.src.connect.datastore import DataStore
from app.src.database.db import Database
#from app.src.database.cache_emb import EmbeddingCache
from app.src.database.db_datasets import DatasetsDB
from app.src.database.cache_query import QueryCache
from app.src.connect.gpt import get_chat_completion_stream, get_chat_completion
from app.src.connect.gpt_v2 import get_chat_completion_v2, get_function_call, get_chat_completion_json, get_chat_completion_stream_v2
from .function_call import get_text_retrieval_function_call
from .functions import retrieve_context_from_datastore, retrieve_context_from_google_search
from .sql import SQLAgent

from app.models.models import Query, Type, Dataset, Related
from app.src.config.prompt.prompt import get_prompt
from app.models.models import Response, Label
from app.models.api_models import MessageResponse


import timeit
import yaml
from loguru import logger
level_agent = logger.level("AGENT", no=38, color="<yellow>", icon="♣")
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
        self.model_basic = 'gpt-3.5-turbo-1106'
        self.model_advanced = 'gpt-4-1106-preview'
        self.cache_query = QueryCache()
        self.db_datasets = DatasetsDB()
        

        with open('app/src/config/schemas.yaml', 'r') as file:
            # Load the content using yaml.load
            data = yaml.load(file, Loader=yaml.FullLoader)
            self.schema = data['schema']
            self.schema_short = data['schema_short']

        with open('app/src/config/datasets.yaml', 'r') as file:
            datasets = yaml.load(file, Loader=yaml.FullLoader)
            self.source = {k: {"source": v['source']} for k, v in datasets.items()}


    # updated
    async def classification_related(self, query: str):
        messages = get_prompt('classification_and_related', query, self.schema_short)

        res = get_chat_completion_json(messages, temperature=1, model=self.model_advanced)

        related = []

        try:
            for r in res['related questions']:
                related.append(Related(query=r["question"], title=r["topic"], sql=r.get("SQL")))


            response = Response(
                code = 200,
                label = Label.database if res.get("original label") == 'Database' else Label.text,
                query = res.get("original question"),
                title = res.get("original topic"),
                related_topics = related
            )

            print(f"Response is: {response}")

            asyncio.create_task(self.cache_query.insert_query(response))

            return response
        except Exception as e:
            print(e)
            return Response(
                code = 404
                )
            
        
    
    

    async def classification(self, query: str) -> Response:
        """
            Get Label(text or database), Title from the query
        """
        schema_short = self.schema_short
        messages = get_prompt('classification', query, schema_short)
        time_start = time.time()
        res = get_chat_completion_json(messages)
        time_end = time.time()

        logger.opt(lazy=True).log("AGENT", f"Classification | Query: {query} | Processing Time: {time_end - time_start} | Response: {res}")

        response = Response(
            code = 200,
            label = Label.database if res.get("label") == 'Database' else Label.text,
            query = query,
            title = res.get('topic'),
        )

        # Insert into cache
        asyncio.create_task(self.cache_query.insert_query(response, query))
        return response
    

    

    async def related(self, query: str):
        schema_short = self.schema_short
        messages = get_prompt('related', query, schema_short)

        start = timeit.default_timer()
        res = get_chat_completion_json(messages)
        end = timeit.default_timer()

        #logger.opt(lazy=True).log("CLASSIFICATION", f"Query: {query} | Processing Time: {end - start} | Response: {res}")

        return res


        
    # updated
    async def query_text(self, query: str, is_streaming: bool = False):

        """
        Generate text response from user queries
        Rely on context retrieved from 2 source: datastore and google search
        """

        time_start = time.time()
        # Generate function specification for text retrieval
        function_call_messages = get_prompt('text_retrieval_function_call', query)
        tools = get_text_retrieval_function_call()
        functions = get_function_call(function_call_messages, tools, model=self.model_advanced)

        # print(f"Function call results: {functions}")

        if functions:
            
            #Retrieve context from datastore
            if 'retrieve_context_from_datastore' in functions.keys():
                fn_name = 'retrieve_context_from_datastore'
                context_datastore = await retrieve_context_from_datastore(functions[fn_name]['query'], 
                                                                    functions[fn_name].get('start_date'), 
                                                                    functions[fn_name].get('end_date')
                                                                    )
            else:
                context_datastore = await retrieve_context_from_datastore(query)

            if 'retrieve_context_from_google_search' in functions.keys():
                fn_name = 'retrieve_context_from_google_search'
                context_search = await retrieve_context_from_google_search(functions[fn_name]['query'], functions[fn_name].get('date_period'))
            else:
                context_search = await retrieve_context_from_google_search(query)


        else:
            context_search = []
            context_datastore = []

        # Combine the context from 2 sources
        context = context_datastore + context_search
        
        # Get list of scores, texts, and sources

        unique_ids = set()
        unique_context = []
        scores = []
        for item in context:
            id = item.id 
            if id not in unique_ids:
                unique_ids.add(id)
                unique_context.append(item)
                scores.append(item.score)

        # Sort the context by score
        sorted_context = sorted(unique_context, key=lambda x: x.score, reverse=True)

        formatted_context = [f"Source: {t.metadata.publisher} \n Content: {t.text}" for t in sorted_context[:15]]

        messages = get_prompt('text', query, '\n\n'.join(formatted_context))

        if is_streaming:

            return get_chat_completion_stream_v2(messages, model=self.model_basic)
        
        else:

    
            res = get_chat_completion_v2(messages, model=self.model_basic)

            time_end = time.time()
            logger.opt(lazy=True).log("AGENT", f"Text | Query: {query} | Processing Time: {time_end - time_start} | Response: {res}")
            
            # upload response to cache
            asyncio.create_task(self.cache_query.insert_text_response(res, query))

            return res
        



    async def query_data(self, query: str) -> Optional[Dict[str, Dict[str, str]]]:
        """
            Get data based on SQL

            Return:
            if success
                {   
                    'status': 'success', 
                    'sql': SQL query,
                    'data': csv data,
                    'explanation': explanation of the data,
                }
            if error;
                {'status': 'failed', 'message': error message}
        """
        sql_agent = SQLAgent(query)
        res = await sql_agent.get_data()

        # upload response to cache
        asyncio.create_task(self.cache_query.insert_data_response(res, query))
        return res
 


    async def query_data_chart(self, query: str, data: str) -> Optional[str]:
        # From data to generate chart code
        time_start_chart = timeit.default_timer()
        messages = get_prompt('data_to_chart', query, data)
        res = get_chat_completion_json(messages)
        time_end_chart = timeit.default_timer()

        # upload response to cache
        asyncio.create_task(self.cache_query.insert_chart_response(res, query))

        #logger.opt(lazy=True).log("SQLECHART", f"Query: {query} | Processing Time: {time_end_chart - time_start_chart} | Response: {res}")

        return res
    

    # Linked to test API endpoint
    async def run_sql(self, query: str):
        db = Database()
        time_start = time.time()
        data = db.execute_query(query)
        time_end = time.time()
        #logger.opt(lazy=True).log("RUNSQL", f"Query: {query} | Processing Time: {stop - start} | Response: {data}")
        return data
    

    async def query_dataset_summary(self, message: Optional[List[Dict[str, str]]]= None, thread_id: Optional[str]=None):
        context = ''
        chat_message = []
        if message:
            # if message is provided, use it
            chat_message = message

        elif thread_id:
            # if message not provide, retrieve message from database by thread_id
            chat_message = await self.db_datasets.get_messages_by_thread_id('data_requests', thread_id)
            
        else:
            print("In order to summarise dataset request, please provide either message or thread_id")
            return None
        
        # Convert to MessageResponse object
        chat_message = [MessageResponse(**m) for m in chat_message]
    
        # Reformat the user and assistant message history, right before Step 3: Notification
        for m in chat_message:
            if m.content.startswith('**Specify Data Source:**'):
                break
            context += f"\"{m.role}\" : \"{m.content}\"\n\n"

        messages = get_prompt('dataset_summary', context=context)
        res = get_chat_completion_json(messages)

        structure = ''
        for col, des in res['column_names'].items():
            structure += f"- **{col}**: {des}\n\n"
        
        return Dataset(name=res['dataset_name'], 
                       description=res['dataset_summary'], 
                       sector=res['tags'], 
                       structure=structure,
                       query=res['queries'],
                       )

    

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
    

    async def query_subtitle_content(self, query: str, table_of_content: str) -> str:
        """
            Generate text analysis based on the subtitle and table of content
            Args:
                query: subtitle
                context: table of content
            Returns:
                {
                    "subtitle": the subtitle, 
                    "content": the text analysis, 
                    "source": the source of the data
                }
        """
        query_class = Query(query=query, top_k=10)
        
        # Retrieve context, keep only above threshold
        context, source = self.datastore.retrieval(query_class)

        # If no context retrieved, resort to ChatGPT
        if len(context) == 0:
            messages = get_prompt('report_content_gpt', query, None, table_of_content)        
        else:
            messages = get_prompt('report_content', query, context ,table_of_content)
        
        res = get_chat_completion_json(messages, self.model_basic)

        # In case the subtitle field from model output is not the same as the original value, overwrite it
        res['title'] = query    
        res['source'] = source if len(source) > 0 else 'Endepth Data Insight'

        return res
    

    

    async def generate_report_content(self, table_of_content: Dict[str, str]):
        table_content_str = json.dumps(table_of_content)

        # Get a list of subtitles
        subtitles = []
        for k, v in table_of_content.items():
            for k1, v1 in v['subtitles'].items():
                subtitles.append(v1)


        # Get the analysis for each subtitle concurrently
        time_start = time.time()
        content_partial = partial(self.query_subtitle_content, table_of_content = table_content_str)
        tasks = [content_partial(subtitle) for subtitle in subtitles]
        contents = await asyncio.gather(*tasks)

        time_end = time.time()

        logger.opt(lazy=True).log("AGENT", f"Generate full report | Processing Time: {time_end - time_start} | Table of Content: {table_content_str} |Response: {contents}")
        
        # Transform the result into a dictionary
        contents_dic = {t['title']: t['content'] for t in contents}

        # Construct the report dictionary
        report = {}

        for k, v in table_of_content.items():
            report[k] = {'title': v['title'], 'content': {}}
            for k1, v1 in v['subtitles'].items():
                report[k]['content'][k1] = {'subtitle': v1, 'content': contents_dic[v1]}

        return report





        
    

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
    