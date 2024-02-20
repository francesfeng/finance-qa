import asyncio
from typing import List, Dict, Optional
from app.models.models import Label
from app.src.database.cache_query import QueryCache
from app.src.runner.agents import Agent

class Controller:
    
    def __init__(self):
        return
    

    async def query(self, query: str):

        cache = QueryCache(query)

        # retrieve query and retrieve related in parallel
        result, related = await asyncio.gather(cache.retrieve_semantic_match(), cache.retrieve_related())

        
        if result:
            res = result[0]
            score = float(result[1])
            res.related_topics = related

            # If score larger than 0.92, it is exact match
            if score > 0.92 and res.response:
                return res

            # Otherwise, get the response
            if res.label:
                res.response = await self.get_response(query, res.label)
                return res

        # No match, get title, labe, text or data response
        else:
            agent = Agent()
            res = await agent.classification(query)
            res.response = await self.get_response(query, res.label)
            res.related_topics = related
        

        return res
    


    async def get_response(self, query: str, label: str):
        """
            Get either text or data/chart response according to the label
        """
        new_label = label 
        agent = Agent()

        response_dict = {}
        if new_label == 'database':
            data_response = await agent.query_data(query)
            response_dict['data'] = data_response
            data = data_response['data']
            if len(data.split('\n')) == 2 or len(data.split('\n')[0].split(',')) ==1:
                new_label = Label.text
            else:
                chart_response = await agent.query_data_chart(query, data)
                response_dict['chart'] = chart_response
            
        if new_label == 'text':
            text_response = await agent.query_text(query)
            response_dict['text'] = text_response

        return response_dict

        


        






        # Retrieve from cache if similar query exists

        # If cached query matches exactly, return the response in cache

        # If doesn't match exactly, generate new response

        # Get title, and label

        # Get 6 related from cache - 3 text, 3 data response

        # 
