from fastapi import APIRouter, Body,HTTPException
from fastapi.responses import StreamingResponse

from app.src.runner.agents import Agent
from app.src.runner.controller import Controller
from app.src.connect.datastore import DataStore
from app.models.api_models import QueryText, Response

from app.models.models import Query

from loguru import logger


router = APIRouter()

router = APIRouter(prefix="/test",
                   tags = ["test"],
                   responses={404: {"description": "Not found"}},
                   )



@router.post("/classify")
async def query_classify(query: QueryText = Body(...)):
    try:
        return await agent.classification_related(query = query.query)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


# Text based on pinecone, streaming
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
    
# Pincone Table to Chart
@router.post("/table_to_chart")
async def query_table_to_chart(querytext: QueryText = Body(...)):
    try:
        return await agent.query_table_to_chart(querytext.query, querytext.data)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    

# Get SQL query
@router.post("/sql")
async def query_sql(querytext: QueryText = Body(...)):
    try:
        return await agent.query_sql(querytext.query)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    

# Run SQL Query
@router.post("/run_sql")
async def run_sql(querytext: QueryText = Body(...)):
    try:
        return await agent.run_sql(querytext.query)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


# Get SQL query, Run SQL Query, and return table
@router.post("/sql_table")
async def query_sql_to_table(querytext: QueryText = Body(...)):
    try:
        return await agent.query_sql_table(querytext.query)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    

# Retrieve text data from pinecone
@router.post("/retrieval")
async def retrieval(querytext: QueryText = Body(...)):
    query = Query(query = querytext.query, top_k=10)
    try:
        return await datastore.query(query)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


# @app.post("/test/query/table_text_non_stream")
# async def query_table_text(querytext: QueryText = Body(...)):
#     try:
#         return await agent.query_text_table(querytext.query, is_streaming=False)
#     except Exception as e:
#         logger.error(e)
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/query/v2")
# async def query_text(querytext: QueryText = Body(...)):
#     """
#     The non-streaming version of the query endpoint for calling Chat GPT
#     """
#     # Contruct query class
#     query = query = Query(
#         query = querytext.query,
#         filter = {"type": Type.table},
#         top_k = 10
#     )
#     try:
#         return await agent.query_non_stream(query = query, model = "table_datastore")
#     except Exception as e:
#         logger.error(e)
#         raise HTTPException(status_code=500, detail=str(e))


@router.on_event("startup")
async def startup():
    global controller
    global agent
    global datastore
    controller = Controller()
    agent = Agent()
    datastore = DataStore()


