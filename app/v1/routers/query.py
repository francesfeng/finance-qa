from fastapi import APIRouter, Body,HTTPException
from fastapi.responses import StreamingResponse
from app.models.api_models import QueryText, Response
from loguru import logger
import json


from app.src.runner.agents import Agent


router = APIRouter(prefix="/query",
                   tags = ["query"],
                   responses={404: {"description": "Not found"}},
                   )


# Send a question, the response get the type, topic, related topics, 
@router.post("/")
async def query(query: QueryText = Body(...)):
    try:
        return await agent.classification_related(query.query)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    
    
# SQL Query to Chart
@router.post("/data_chart")
async def query_data_to_chart(querytext: QueryText = Body(...)):
    try:
        return await agent.query_data_chart(querytext.query, querytext.data)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    


# Gete text, which is composed of text and markdown table
@router.post("/text")
async def query_text(querytext: QueryText = Body(...)):
    try:
        return StreamingResponse(
            await agent.query_text(query = querytext.query, is_streaming=True), 
            media_type="text/event-stream"
            )
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.post("/data")
async def query_data(querytext: QueryText = Body(...)):
    try:
        return await agent.query_data(querytext.query)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    
    



@router.on_event("startup")
async def startup():
    global agent
    agent = Agent()
