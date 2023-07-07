import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel
from app.src.controller import Controller

# Define the model. TODO: move to seperate models.api file
class Query(BaseModel):
    query: str

class Response(BaseModel):
    type: str
    response: str

bearer_scheme = HTTPBearer()
BEARER_TOKEN = os.environ.get("BEARER_TOKEN")
assert BEARER_TOKEN is not None


def validate_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    if credentials.scheme != "Bearer" or credentials.credentials != BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return credentials


app = FastAPI(dependencies=[Depends(validate_token)])

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
async def query(query: Query = Body(...)):
    try:
        result = controller.run(query.query)
        return Response(**result)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.on_event("startup")
async def startup():
    global controller
    controller = Controller()


@app.get("/healthcheck")
def read_root():
    return {"status": "ok"}


def start():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)