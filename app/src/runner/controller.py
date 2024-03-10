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
        # use both exact match and semantic match to retrieve the response, in case the embeddings in the semantic match is not available
        result1, result_comb, related = await asyncio.gather(cache.retrieve_exact_match(query), cache.retrieve_semantic_match(), cache.retrieve_related())
        
        # if exact match is not available, use semantic match
        result2 = result_comb[0]
        score = result_comb[1]
        result = result1 or result2
        agent = Agent()

        is_result = False

        # if result is not None and result[1] > 0.92, return the result
        if result1 or (result2 and float(score) > 0.92):
            is_result = True

        # If none of the response or related is valid, generate both in parallel
        if not is_result and not related:
            res, related = await asyncio.gather(agent.query_text_json(query), agent.related(query))
            res.related_topics = related

        else:
            # if response is not valid, regenerate response
            if not is_result:
                res = await agent.query_text_json(query)
            else:
                res = result
            
            # if related_topics is not valid, regenerate related_topics
            if related:
                res.related_topics = related
            else:
                res.related_topics = await agent.related(query)
        
        return res

        
    async def re_generate(self, query: str):
        """
            Generate response and related topics
            Skip retrieving from cache
            The new result will regresh the cache
        """
        agent = Agent()
        res, related = await asyncio.gather(agent.query_text_json(query), self.get_related(query))
        res.related_topics = related

        return res
    

    async def get_related(self, query: str):
        """"
            Get a list of related topics
            if not in cache, regenerate from agent
        """
        cache = QueryCache(query)
        related = await cache.retrieve_related()

        # This step is redundant, but the retrieved related always has 6 results, regardless the similarity
        if not related:
            agent = Agent()
            related = await agent.related(query)
        return related