import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel
from typing import List
from src.controller import Controller
from src.models.models import Query, Type
from src.models.agents import Agent
from src.connect.gpt import test_query

# Define the model. TODO: move to seperate models.api file
class QueryText(BaseModel):
    query: str

class RelatedTopic(BaseModel):
    query: str
    title: str
    label: str

class Response(BaseModel):
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
        return Response(**result)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@app.post("/query/v1")
async def query_table(querytext: QueryText = Body(...)):
    # Contruct query class
    query = query = Query(
        query = querytext.query,
        filter = {"type": Type.table},
        top_k = 10
    )
    try:
        return StreamingResponse(
            await agent.query_text_table(query = query, model = "table_datastore"), 
            media_type="text/event-stream"
            )
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@app.post("/query/v2")
async def query_text(querytext: QueryText = Body(...)):
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
        raise HTTPException(status_code=500, detail="Internal Server Error")

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