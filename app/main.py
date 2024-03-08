from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.dependencies import bearer_scheme
from app.v1.routers import query
from app.v1.routers import assistant
from app.v1.test import test
from app.v1.routers import message
from mangum import Mangum
from loguru import logger
import sys


app = FastAPI()
# app = FastAPI(dependencies=[Depends(bearer_scheme)])

# origins = [
#     "http://localhost:8765",
#     "http://localhost:8000/",
#     "http://localhost"
#     ]

app.add_middleware(
    CORSMiddleware,
    allow_origins='*',
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["x-apigateway-header", "Content-Type", "X-Amz-Date"],
)



@app.get("/")
async def root():
    logger.add(sys.stderr, enqueue=True)
    logger.add("../logs/file_1.log", rotation="500 MB")    #TODO: not write to log file
    return {"message": "Welcome to Endepth!"}

app.include_router(query.router, prefix="/v1")
app.include_router(assistant.router, prefix="/v1")
app.include_router(message.router, prefix="/v1")
app.include_router(test.router)

handler = Mangum(app=app, lifespan="on")

# def start():
#     uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

#--------------------------------------------------------------------------
# Version 1 endpoints
""" 
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
"""


