from fastapi import APIRouter, Body,HTTPException
from fastapi.responses import StreamingResponse
from app.models.api_models import Query, QueryThread, MessageResponse, MessageFileResponse
from app.src.assistant.data_assistant import DataAssistant
from app.src.assistant.analyst_assistant import AnalystAssistant
from app.src.database.db_datasets import DatasetsDB
from loguru import logger
import io
import json

router = APIRouter(prefix="/assistant",
                   tags = ["assistant"],
                   responses={404: {"description": "Not found"}},
                   )

@router.post("/create_data_assistant")
async def new_data_assistant():
    try:
        assistant = DataAssistant(model='advanced')
        return await assistant.create_assistant()
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/data_query") 
async def data_query(query: QueryThread = Body(...)):
    try: 
        assistant = DataAssistant(model='advanced')
        res = await assistant.submit_query(query.assistant_id, query.thread_id, query.query)
        return MessageResponse(**res)
    
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/create_analyst_assistant")
async def new_analyst_assistant(query: Query = Body(...)):
    try:
        # query is the dataset name
        assistant = AnalystAssistant(model='advanced')
        return await assistant.create_assistant(query.query)
        
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/analyst_query")
async def analyst_query(query: QueryThread = Body(...)):
    try:
        assistant = AnalystAssistant(model='advanced')
        response = await assistant.submit_query(query.assistant_id, query.thread_id, query.query)
        return [MessageFileResponse(**message) for message in response if message['role'] == 'assistant']
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/retrieve_image")

async def retrieve_image(query: Query = Body(...)):
    try:
        db = DatasetsDB()
        image_bytes = await db.get_image_bytes(query.query)
        return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png")
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))





