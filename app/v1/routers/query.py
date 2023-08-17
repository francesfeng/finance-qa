from fastapi import APIRouter, Body,HTTPException
from fastapi.responses import StreamingResponse
from app.models.api_models import QueryText, Response
from loguru import logger


from src.models.agents import Agent
from src.models.controller import Controller


router = APIRouter(prefix="/query",
                   tags = ["query"],
                   responses={404: {"description": "Not found"}},
                   )


# Send a question, the response get the type, topic, related topics, 
@router.post("/")
async def query(query: QueryText = Body(...)):
    try:
        result = await controller.run_query(query.query)
        return Response(**result.dict())
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    
    
# SQL Query to Chart
@router.post("/sql_chart")
async def query_sql_to_chart(querytext: QueryText = Body(...)):
    try:
        return await agent.query_sql_chart(querytext.query, querytext.data)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    


# Gete text, which is composed of text and markdown table
@router.post("/text")
async def query_combined(querytext: QueryText = Body(...)):
    try:
        return StreamingResponse(
            await agent.query_combined(query = querytext.query, is_streaming=True), 
            media_type="text/event-stream"
            )
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    

# Table based on pincone text, streaming
@router.post("text_table")
async def query_table(querytext: QueryText = Body(...)):
    try:
        return StreamingResponse(
            await agent.query_text_table(query = querytext.query, is_streaming=True), 
            media_type="text/event-stream"
            )
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    

# Pincone SQL Table to Chart
@router.post("/table_to_chart")
async def query_table_to_chart(querytext: QueryText = Body(...)):
    try:
        return await agent.query_table_to_chart(querytext.query, querytext.data)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    


@router.on_event("startup")
async def startup():
    global controller
    global agent
    controller = Controller()
    agent = Agent()