import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from controller import Controller


class Query(BaseModel):
    query: str

class Response(BaseModel):
    type: str
    response: str

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, welcome to EnDepth"}


@app.post("/query", response_model=Response)
async def query(query: Query):
    result = controller.run(query.query)
    return result


@app.on_event("startup")
async def startup():
    global controller
    controller = Controller()


def start():
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)