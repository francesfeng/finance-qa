from fastapi import APIRouter, Body,HTTPException
from fastapi.responses import StreamingResponse
from app.models.api_models import QueryText, Response
from loguru import logger
import json
import sys


from app.src.runner.agents import Agent
from app.src.runner.controller import Controller


router = APIRouter(prefix="/query",
                   tags = ["query"],
                   responses={404: {"description": "Not found"}},
                   )


@router.post("/")
async def query(query: QueryText = Body(...)):
    """
    Get the entire response, retrieve from cache if available
    """
    try: 
        return await controller.query(query.query)
    except Exception  as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/get_response")
async def query(query: QueryText = Body(...)):
    """
    Construct new response based on given query and label
    """
    try: 
        return await controller.get_response(query = query.query, label= query.data)
    except Exception  as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    

# Send a question, the response get the type, topic, related topics, 
@router.post("/classification")
async def query(query: QueryText = Body(...)):
    try:
        res = await agent.classification_related(query.query)
        return Response(**res.__dict__)
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
@router.post("/text_streaming")
async def query_text_streaming(querytext: QueryText = Body(...)):
    try:
        return StreamingResponse(
            await agent.query_text(query = querytext.query, is_streaming=True), 
            media_type="text/event-stream"
            )
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/text")
async def query_text(querytext: QueryText = Body(...)):
    try:
        return await agent.query_text(querytext.query, is_streaming=False)
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
    
    
@router.post("/dataset_summary")
async def query_dataset_summary(querytext: QueryText = Body(...)):
    """
        Create a dataset summary based on the chat messages or thread_id

        - **query**: the thread_id 
        - **data**: the chat messages, is JSON format
    """
    try:
        print(f"query: {querytext.query}, data: {querytext.data}")
        thread_id = querytext.query 
        message = None
        if querytext.data:
            try:
                message = json.loads(querytext.data) 
            except Exception as e:
                message = None
            None

        return await agent.query_dataset_summary(message=message, thread_id=thread_id)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.on_event("startup")
async def startup():
    global agent, controller
    agent = Agent()
    controller = Controller()
