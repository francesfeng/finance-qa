import json
import timeit
from app.src.runner.agents import Agent
from app.models.models import Response, ResponseType, Label

#from loguru import logger
#logger.add("file_prompt.log", rotation="12:00")  
#level_response = logger.level("RESPONSE", no=38, color="<yellow>", icon="♣")

class Controller:

    def __init__(self):
        self.agent = Agent()

    async def run_query(self, query: str) -> Response:

        start = timeit.default_timer()
        res_json = await self.agent.classification_related(query)
        classify = None
        data = None
        text = None

        try:
            #res_json = json.loads(res)
            classify = res_json['original label']
            title = res_json['original topic']
            related =  [{'query': i['question'], 'title': i['topic']} for i in res_json['related questions']]
        # When there is JSONDecodeError, assume the classification is Text 
        except Exception as e:
            #logger.error(f"Query: {query} | Error: {e}")
            classify = 'Text'
            title = query
            related = None


        if classify == 'Database':
            sql = await self.agent.query_sql(query)

            if sql.startswith('Error'):
                classify = 'Text'

        if classify == 'Database':
            data = await self.agent.run_sql(sql)

            data_len = len(data.split('\r\n'))

            # If data is empty, change label to Text and re-run as text query
            if data_len == 1:
                classify = 'Text'

            elif data_len == 2:
                text = await self.agent.query_data_to_text(query, data)
                #stop = timeit.default_timer()
                return Response(
                    code=200, 
                    type=ResponseType.textdata, 
                    label=Label.database, 
                    query=query, 
                    title=title,
                    response=text,                         
                    related_topics=related
                )
                #logger.opt(lazy=True).log("RESPONSE", f"Query: {query} | Processing Time: {stop - start} | Response: {response}")
                    
                
            else:
                # Need to further process to generate chart code
                #stop = timeit.default_timer()
                return Response(
                    code=200, 
                    type=ResponseType.data, 
                    label=Label.database, 
                    query=query, 
                    title=title,
                    response=data,
                    related_topics=related
                )
                    #logger.opt(lazy=True).log("RESPONSE", f"Query: {query} | Processing Time: {stop - start} | Response: {response}")
                    
                
        else:
            text_type = await self.agent.classify_text(query)
            if text_type == 'error':
                response = Response(
                    code=500,
                    type=ResponseType.error,
                    label = Label.text,
                    query=query,
                    related_topics=related
                )
            if text_type == 'text':
                response = Response(
                    code=200,
                    type=ResponseType.text,
                    label = Label.text,
                    query=query,
                    title=title,
                    related_topics=related
                )
            if text_type == 'table':
                response = Response(
                    code=200,
                    type=ResponseType.table,
                    label = Label.text,
                    query=query,
                    title=title,
                    related_topics=related
                )
            #stop = timeit.default_timer()
            #logger.opt(lazy=True).log("RESPONSE", f"Query: {query} | Processing Time: {stop - start} | Response: {response}")
        
        return response
        
                    
