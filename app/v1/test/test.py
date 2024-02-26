from fastapi import APIRouter, Body,HTTPException
from fastapi.responses import StreamingResponse

from app.src.runner.agents import Agent
from app.src.connect.datastore import DataStore
from app.models.api_models import QueryText, Query


from loguru import logger


router = APIRouter()

router = APIRouter(prefix="/test",
                   tags = ["test"],
                   responses={404: {"description": "Not found"}},
                   )



# Run SQL Query
@router.post("/run_sql")
async def run_sql(querytext: Query = Body(...)):
    """
    Run SQL Query, output CSV data string format
    """
    try:
        return await agent.run_sql(querytext.query)
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
    global agent
    agent = Agent()


