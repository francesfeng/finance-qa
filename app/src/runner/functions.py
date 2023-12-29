import time
import asyncio
from typing import Optional
from app.models.models import Query, DocumentMetadataFilter 
from app.src.connect.datastore import DataStore
from app.src.search.google import GoogleSearch

from loguru import logger
logger_function = logger.level("FUNCTION_CALL", no=33, color="<green>", icon="♣")

async def retrieve_context_from_datastore(query: str, 
                                    start_date: Optional[str]=None, 
                                    end_date: Optional[str]=None):
    """
    Retrieve context from vector datastore based on the query
    Args:
        query: The query to retrieve context, 
        start_date: The date from which the context is retrieved. 
        end_date: The date to which the context is retrieved.

    Returns:
        text: The text retrieved from datastore
        source: The source of the text retrieved from datastore
    """

    # Create a filter and query object   

    if start_date or end_date:
        filter = DocumentMetadataFilter(start_date=start_date, end_date=end_date)
        query_class = Query(query=query, filter = filter, top_k=10)
    else:
        query_class = Query(query=query, top_k=10)

    # Retrieve data from datastore
    time_start = time.time()
    datastore = DataStore()
    context = datastore.query(query_class)
    time_end = time.time()

    logger.opt(lazy=True).log("FUNCTION_CALL", f"retrieve_context_from_datastore | Query: {query} | start_date: {start_date} | end_date: {end_date} | Processing time: {time_end - time_start} seconds | Context length: {len(context)}")
    
    return context



async def retrieve_context_from_google_search(query: str, date_period: Optional[str]=None):
    """
    Generate 3 google search queries, to retrieve context from google search based on the search queries
    """
    queries = [q.strip() for q in query.split(",")]

    time_start = time.time()
    search = GoogleSearch(query = queries, date_period=date_period)
    context = search.run()
    time_end = time.time()

    logger.opt(lazy=True).log("FUNCTION_CALL", f"retrieve_context_from_google | Query: {query} | date_period: {date_period} | Processing time: {time_end - time_start} seconds | Context length: {len(context)}")
    

    return context




