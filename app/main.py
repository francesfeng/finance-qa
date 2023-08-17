import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel
from typing import List
#from src.controller import Controller
from src.models.models import Query, Type, Response
from src.models.agents import Agent
from src.models.controller import Controller
from src.connect.gpt import test_query


# Define the model. TODO: move to seperate models.api file
class QueryText(BaseModel):
    query: str
    data: str = None

class RelatedTopic(BaseModel):
    query: str
    title: str
    label: str

class ResponseFull(BaseModel):
    code: int
    type: str
    label: str
    query: str
    title: str
    response: str
    related_topics: List[RelatedTopic]

bearer_scheme = HTTPBearer()
# BEARER_TOKEN = os.environ.get("BEARER_TOKEN")
# assert BEARER_TOKEN is not None


# def validate_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
#     if credentials.scheme != "Bearer" or credentials.credentials != BEARER_TOKEN:
#         raise HTTPException(status_code=401, detail="Invalid or missing token")
#     return credentials


app = FastAPI(dependencies=[Depends(bearer_scheme)])

origins = [
    "http://localhost:8765",
    "http://localhost:8000/",
    "http://localhost"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello, welcome to EnDepth"}


@app.post("/query")
async def query(query: QueryText = Body(...)):
    try:
        result = controller.run(query.query)
        return ResponseFull(**result)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))

#--------------------------------------------------------------------------
# Version 1 endpoints

@app.post("/v1/query")
async def query(query: QueryText = Body(...)):
    try:
        result = await controller.run_query(query.query)
        return Response(**result.dict())
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


#--------------------------------------------------------------------------
# Following are test endpoints for the new agent

@app.post("/test/query/classify")
async def query_classify(query: QueryText = Body(...)):
    try:
        return await agent.classification(query = query.query)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/test/query/combined")
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
@app.post("/test/query/text_table")
async def query_table(querytext: QueryText = Body(...)):
    try:
        return StreamingResponse(
            await agent.query_text_table(query = querytext.query, is_streaming=True), 
            media_type="text/event-stream"
            )
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))

# Text based on pinecone, streaming
@app.post("/test/query/text")
async def query_text(querytext: QueryText = Body(...)):
    try:
        return StreamingResponse(
            await agent.query_text(query = querytext.query, is_streaming=True), 
            media_type="text/event-stream"
            )
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    

# Pincone Table to Chart
@app.post("/test/query/table_to_chart")
async def query_table_to_chart(querytext: QueryText = Body(...)):
    try:
        return await agent.query_table_to_chart(querytext.query, querytext.data)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    

# Get SQL query
@app.post("/test/query/sql")
async def query_sql(querytext: QueryText = Body(...)):
    try:
        return await agent.query_sql(querytext.query)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    

# Run SQL Query
@app.post("/test/query/run_sql")
async def run_sql(querytext: QueryText = Body(...)):
    try:
        return await agent.run_sql(querytext.query)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


# Get SQL query, Run SQL Query, and return table
@app.post("/test/query/sql_table")
async def query_sql_to_table(querytext: QueryText = Body(...)):
    try:
        return await agent.query_sql_table(querytext.query)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))



# SQL Query to Chart
@app.post("/test/query/sql_chart")
async def query_sql_to_chart(querytext: QueryText = Body(...)):
    try:
        return await agent.query_sql_chart(querytext.query, querytext.data)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/test/query/table_text_non_stream")
async def query_table_text(querytext: QueryText = Body(...)):
    try:
        return await agent.query_text_table(querytext.query, is_streaming=False)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/v2")
async def query_text(querytext: QueryText = Body(...)):
    """
    The non-streaming version of the query endpoint for calling Chat GPT
    """
    # Contruct query class
    query = query = Query(
        query = querytext.query,
        filter = {"type": Type.table},
        top_k = 10
    )
    try:
        return await agent.query_non_stream(query = query, model = "table_datastore")
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))

# @app.post("/query/demo")
# async def query_demo(num: int = Body(...)):
#     return StreamingResponse(test_query(num), media_type="text/event-stream")



@app.on_event("startup")
async def startup():
    global controller
    global agent
    controller = Controller()
    agent = Agent()


@app.get("/healthcheck")
def read_root():
    return {"status": "ok"}


def start():
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)