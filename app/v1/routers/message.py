from fastapi import APIRouter, Body,HTTPException
from app.models.api_models import QueryText
from app.src.database.cache_query import QueryCache
from loguru import logger
import io
import json


router = APIRouter(prefix="/messages",
                   tags = ["messages"],
                   responses={404: {"description": "Not found"}},
                   )


@router.post("/retrieve_message_by_query")
async def retrieve_message_by_query(query: QueryText = Body(...)):
    """
    Args:
        query (QueryText): The query text and response type to retrieve the message for.
        There are 3 response types: "text", "data" or "chart"
        
    Returns:
        The retrieved message matching the query and response type.
        the retrieved message is - 
        markdown text if response type is "text"
        dictionary if response type is "data", which includes data (in csv format), source and explanation 3 fields
        json (echarts specification) if response type is "chart"
        
    Raises:
        HTTPException: If there is an error retrieving the message.
    """
    try:
        return await db.retrieve_exact_match_response(query=query.query, response_type=query.data)
    
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.on_event("startup")
async def startup():
    global db
    db = QueryCache()