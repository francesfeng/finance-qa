import asyncpg
import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.src.config.config import Config
from app.models.models import Response, Label, Related
from app.src.utils.hash import text_to_hash
from app.src.connect.gpt_v2 import get_embeddings_v2
from app.src.utils.similarity import cosine_similarity
from loguru import logger

level_query_cache = logger.level("QUERYCACHE", no=38, color="<blue>", icon="♣")


host = os.environ['NEON_HOST']
user = os.environ['NEON_USER']
password = os.environ['NEON_PASSWORD']
database = 'datasets'

class QueryCache:

    def __init__(self, query: Optional[str] = None, config_path: Optional[str] = None):
        config = Config(config_path)
        self.model_embed = config.model_embed
        self.query_similarity_threshold = config.query_similarity_threshold
        self.embedding_dimension = config.embedding_dimension


        if query:
            self.query = query.strip()
            self.query_hash = text_to_hash(self.query)
            self.query_emb, self.query_emb_str = self.__create_emb_str(self.query)
        return
    
    async def create_connection(self):
        self.conn = await asyncpg.connect(host=host, database=database, user=user, password=password)
     

    async def insert_classification(self, response: Response, query: Optional[str] = None):
        """
            Insert user query, query title, label, related questions to query cache table
        """
        

        # Set query hash and query embedding if query is not set in class
        if not hasattr(self, 'query') and query:
            self.query = query.strip()
            self.query_hash = text_to_hash(self.query)
            self.query_emb, self.query_emb_str = self.__create_emb_str(self.query)


        try:
            await self.create_connection()

            sql_query = """
            INSERT INTO queries (query, query_hash, title, label, related, query_embedding, created_at) 
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (query_hash) DO
            UPDATE SET query = EXCLUDED.query, query_hash = EXCLUDED.query_hash, title = EXCLUDED.title, label = EXCLUDED.label, related = EXCLUDED.related, query_embedding = EXCLUDED.query_embedding, created_at = EXCLUDED.created_at;
            """
            
            
            await self.conn.execute(sql_query, 
                                    self.query, 
                                    self.query_hash, 
                                    response.title, 
                                    response.label, 
                                    json.dumps([r.__dict__ for r in response.related_topics]) if response.related_topics else None, 
                                    self.query_emb_str,
                                    datetime.utcnow())
        except Exception as e:
            logger.error(f"Insert the classification results | Error in inserting classification results in query_Cache: {e}")
        finally:
            await self.conn.close()

        return
    

    async def insert_related(self, related: List[Related], query: Optional[str] = None):
        if not hasattr(self, 'query') and query:
            self.query = query.strip()
            self.query_hash = text_to_hash(self.query)
            #self.query_emb, self.query_emb_str = self.__create_emb_str(self.query)

        try:
            await self.create_connection()

            sql_query = """
            INSERT INTO queries (query, query_hash, related, created_at) 
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (query_hash) DO
            UPDATE SET related = EXCLUDED.related, created_at = EXCLUDED.created_at;
            """

            await self.conn.execute(sql_query, 
                                    self.query, 
                                    self.query_hash,                                   
                                    json.dumps([r.__dict__ for r in related]), 
                                    datetime.utcnow())
        except Exception as e:
            logger.error(f"Insert the classification results | Error in inserting classification results in query_Cache: {e}")
        finally:
            await self.conn.close()
        return 


    

    async def insert_text_response(self, response: Response, query: Optional[str] = None):
        """
            Insert text response by looking up the query hash value
        """
        # Set query hash and query embedding if query is not set in class
        if not hasattr(self, 'query') and query:
            self.query = query.strip()
            self.query_hash = text_to_hash(self.query)
            self.query_emb, self.query_emb_str = self.__create_emb_str(self.query)

        try:
            await self.create_connection()
            sql_query = """
            INSERT INTO queries (query, query_hash, title, label, text_response, query_embedding, created_at) 
            VALUES ($1, $2, $3, $4, $5, $6, $7) 
            ON CONFLICT (query_hash) DO 
            UPDATE SET query = EXCLUDED.query, 
                query_hash = EXCLUDED.query_hash, 
                title = EXCLUDED.title, 
                label = EXCLUDED.label, 
                text_response = EXCLUDED.text_response, 
                query_embedding = EXCLUDED.query_embedding, 
                created_at = EXCLUDED.created_at;
            
            """
            await self.conn.execute(sql_query, 
                                    self.query, 
                                    self.query_hash, 
                                    response.title,
                                    response.label,
                                    response.response['text'],
                                    self.query_emb_str, 
                                    datetime.utcnow(),
                                    )
        except Exception as e:
            logger.error(f"Insert the text response | Error in inserting text response in query_Cache: {e}")
        finally:
            await self.conn.close()
        return 
    


    async def insert_data_response(self, response: Dict[str, Any], query: Optional[str] = None):
        """
            Insert data response by looking up the query hash value
        """
        # Set query hash and query embedding if query is not set in class
        if not hasattr(self, 'query') and query:
            self.query = query.strip()
            self.query_hash = text_to_hash(self.query)

        await self.create_connection()
        sql_query = """
        INSERT INTO queries (query, query_hash, data_response, sql, data_source, data_explanation)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (query_hash) DO
        UPDATE SET query = EXCLUDED.query, query_hash = EXCLUDED.query_hash, data_response = EXCLUDED.data_response, sql = EXCLUDED.sql, data_source = EXCLUDED.data_source, data_explanation = EXCLUDED.data_explanation;
        
        """
        await self.conn.execute(sql_query, self.query, self.query_hash, response['data'], response['sql'], response['source'] , json.dumps(response['explanation']))
        return

    

    async def insert_chart_response(self, response: Dict[str, Any], query: Optional[str] = None):
        """
            Insert chart response by looking up the query hash value
        """
        
        # Set query hash and query embedding if query is not set in class
        if not hasattr(self, 'query') and query:
            self.query = query.strip()
            self.query_hash = text_to_hash(self.query)


        await self.create_connection()
        sql_query = """
        INSERT INTO queries (query, query_hash, chart_response)
        VALUES ($1, $2, $3)
        ON CONFLICT (query_hash) DO
        UPDATE SET query = EXCLUDED.query, query_hash = EXCLUDED.query_hash, chart_response = EXCLUDED.chart_response;
        """
        await self.conn.execute(sql_query, self.query, self.query_hash, json.dumps(response))
        return
    


    async def retrieve_exact_match(self, query: Optional[str] = None):
        """
            Retrieve the query and the response by matching query_hash exactly
            Useful when user clicked the query from the recommended cache
        """
        if not hasattr(self, 'query') and query:
            self.query = query.strip()
            self.query_hash = text_to_hash(self.query)

        sql_query = f"""
            SELECT query, title, label, text_response, data_response, sql, data_source, data_explanation, chart_response
            FROM queries
            where query_hash = '{self.query_hash}'
        """
        await self.create_connection()
        results = await self.conn.fetch(sql_query)

        if len(results) > 0:
            result = results[0]
            return self.__convert_response(result) 

        else:
            return





    async def retrieve_semantic_match(self, query: Optional[str] = None):
        """
            Retrieve top similar queries from the query cach, 
            Return Response result (if cosline similarity above threshold) and score
        """

        # Set query hash and query embedding if query is not set in class
        if not hasattr(self, 'query') and query:
            self.query = query.strip()
            self.query_emb, self.query_emb_str = self.__create_emb_str(self.query)


        sql_query = f"""
            SELECT query, title, label, text_response, data_response, sql, data_source, data_explanation, chart_response, query_embedding ,l2_distance(query_embedding, '{self.query_emb_str}'::VECTOR(256)) AS similarity
            FROM queries WHERE query_embedding IS NOT NULL
            ORDER BY query_embedding <-> '{self.query_emb_str}'::VECTOR(256)
            LIMIT 1
        """
        await self.create_connection()
        results = await self.conn.fetch(sql_query)

        if len(results) > 0:
            result = results[0]
            # convert embedding from string to float
            emb = self.__convert_emb_to_float(result[-2])

            # calculate cosline similarity query and top retrieved result 
            cosine_score = cosine_similarity(self.query_emb, emb)
            score = float(1- result[-1])
            logger.opt(lazy=True).log('QUERYCACHE', f"RETRIEVEL_TOP | Query: {self.query} | L2 score: {score} | Cosine score: {cosine_score}")

            # Return result when cosine score above threshold
            if cosine_score > self.query_similarity_threshold:
                response = self.__convert_response(result)
                response.query = self.query
                
                return response, cosine_score
        
        return None
    


    async def retrieve_related(self, query: Optional[str] = None):
        """
            Retrieve the top 6 matched quries, excluding the first one
            The retrieved results didn't go through the similarity threshold
        """

        # Set query hash and query embedding if query is not set in class
        if not hasattr(self, 'query') and query:
            self.query = query.strip()
            self.query_emb, self.query_emb_str = self.__create_emb_str(self.query)


        # Get top 6 matches excluding the first one
        sql_query = f"""
            SELECT query, title, label ,l2_distance(query_embedding, '{self.query_emb_str}'::VECTOR(256)) AS similarity
            FROM queries WHERE query_embedding IS NOT NULL
            ORDER BY query_embedding <-> '{self.query_emb_str}'::VECTOR(256)
            OFFSET 1 LIMIT 6
        """
        await self.create_connection()
        results = await self.conn.fetch(sql_query)

        #TODO: add score filter 

        #Reformat to Related class
        if len(results) > 0:
            related = []
            for r in results:
                related.append(Related(query = r[0], title = r[1]))
            logger.opt(lazy=True).log('QUERYCACHE', f"RETRIEVEL_RELATED | Query: {self.query} | Results: {len(results)} | Highest L2 score: {results[0][-1]} | Lowest L2 score: {results[-1][-1]}")
            return related
        
        return
    

    

    def __create_emb_str(self, query: str):
        query_emb = get_embeddings_v2([query], self.model_embed, dimension=self.embedding_dimension)[0]
        query_emb_str = '[' + ','.join(map(str, query_emb)) + ']'
        return query_emb, query_emb_str
    


    def __convert_response(self, result: asyncpg.Record):
        
        label = Label.text if result[2] == 'database' else 'text' 

        response = {}
        if result[3] and result[3] != '':
            response['text'] = result[3]
            label = Label.text

        if result[4] and result[4] != '':
            response['data'] = {'data': result[4], 'sql': result[5], 'source': result[6], 'explanation': result[7]}
            label = Label.database

        if result[8] and result[8] != '':
            response['chart'] = result[8]


        return Response(
                code = 200,
                label = label,
                query = result[0],
                title = result[1],
                response = response,
            )
    


    def __convert_emb_to_float(self, emb_str: str):
        emb = emb_str[2:-2]
        emb_lst = emb.split(',')
        emb_lst = [i for i in map(float, emb_lst)]
        return emb_lst
    



    async def get_related_sql(self):
        """
            Retrieve related questions from the cache, that are a SQL(database) question
        """
        sql_query = "SELECT related FROM queries WHERE related IS NOT NULL"

        await self.create_connection()
        results = await self.conn.fetch(sql_query)

        queries = []
        for r in results:
            if r[0] != 'null':
                queries.extend(json.loads(r[0])) 


        return [r for r in queries if r['sql'] != '']




        









    

