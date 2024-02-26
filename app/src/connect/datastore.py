from typing import List, Optional, Dict, Any
import pinecone
import os
import time

from app.src.config.config import Config
from app.models.models import Query, QueryWithEmbedding, DocumentMetadataFilter, DocumentChunkWithScore
from app.src.connect.gpt import get_embeddings
from app.src.connect.gpt_v2 import get_embeddings_v2
from app.src.utils.date import to_unix_timestamp, to_datestr

from loguru import logger
level_datastore = logger.level("DATASTORE", no=12, color="<green>", icon="♣")

# Read environment variables for Pinecone configuration
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.environ.get("PINECONE_ENVIRONMENT")
PINECONE_INDEX = os.environ.get("PINECONE_INDEX")
assert PINECONE_API_KEY is not None
assert PINECONE_ENVIRONMENT is not None
assert PINECONE_INDEX is not None

class DataStore:

    def __init__(self, config_path: str = None):
        """
        Initialise the datastore.
        """
        pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
        self.index = pinecone.Index(PINECONE_INDEX)

        config = Config(config_path)
        self.similarity_threshold = config.similarity_threshold
        self.model_embed = config.model_embed
        self.embedding_dimension = config.embedding_dimension


    def query(self, query: Query):
        """
        Takes in a list of queries and filters and returns a list of query results with matching document chunks and scores.
        """

        # get a list of just the queries from the Query list
        # Need to change dimensions to 256 once redid embedding
        embeddings = get_embeddings_v2([query.query], model=self.model_embed, dimension=1536)

        # Hydrate the query list with the embeddings
        queries_with_embeddings = QueryWithEmbedding(**query.dict(), embedding=embeddings[0])

        pinecone_filter = self._get_pinecone_filter(query.filter)

        time_start = time.time()
        try:
            response = self.index.query(
                vector = queries_with_embeddings.embedding,
                filter = pinecone_filter,
                top_k = queries_with_embeddings.top_k,
                include_metadata = True
            )
        except Exception as e:
            print(f"Error querying Pinecone: {e}")
            raise e
        
        time_end = time.time()
        
        query_results: List[DocumentChunkWithScore] = []
        results = response["matches"]

        for result in results:
            score = result.score
            if score >= self.similarity_threshold:
                metadata = result.metadata
                metadata_without_text = (
                    {k: v for k, v in metadata.items() if k not in ["text"]}
                    if metadata
                    else None)
                
                result = DocumentChunkWithScore(
                    id=result.id,
                    text=metadata["text"] if metadata and "text" in metadata else None,
                    score=score,
                    metadata=metadata_without_text,
                )

                query_results.append(result)

        logger.opt(lazy=True).log("DATASTORE", f"Query: {query} | Total Retrieved: {len(results)} | Above Threshold: {len(query_results)} | Threshold: {self.similarity_threshold} | Processing Time: {time_end - time_start}")

        return query_results



    def _get_pinecone_filter(
            self, filter: Optional[DocumentMetadataFilter] = None
        ) -> Dict[str, Any]:
        if filter is None:
            return {}

        pinecone_filter = {}

        # For each field in the MetadataFilter, check if it has a value and add the corresponding pinecone filter expression
        # For start_date and end_date, uses the $gte and $lte operators respectively
        # For other fields, uses the $eq operator
        for field, value in filter.dict().items():
            if value is not None:
                if field == "start_date":
                    pinecone_filter["created_at"] = pinecone_filter.get("created_at", {})
                    pinecone_filter["created_at"]["$gte"] = to_unix_timestamp(value)
                elif field == "end_date":
                    pinecone_filter["created_at"] = pinecone_filter.get("created_at", {})
                    pinecone_filter["created_at"]["$lte"] = to_unix_timestamp(value)
                else:
                    pinecone_filter[field] = value

        return pinecone_filter
    

    # def format_response(self, response: List[DocumentChunkWithScore], threshold: float = 0.8) -> List[str]:
    #     """
    #     Takes in the pinecone response, format into created_at ---- text.
    #     Only keep retrieved text with score > 0.8.
    #     """
    #     context = [f"{to_datestr(i.metadata.created_at)} ---- {i.text}" for i in response if i.score > 0.8]
    #     source = [i.metadata.publisher for i in response if i.score > threshold]
    #     source = list(set(source))
    #     return context, source


    # def combine_sort_retrieval(self, res1: List[DocumentChunkWithScore], res2: List[DocumentChunkWithScore]) -> List[str]:
    #     """
    #     Combine the results from two queries and sort by score.
    #     """
    #     res = res1 + res2
    #     res.sort(key=lambda x: x.score, reverse=True)
    #     return self.format_response(res)
    

    # def retrieval(self, query: Query) -> List[str]:
    #     """
    #     A wrapper function, retrieve the context, and reformat the result, keep only output with score above threshold.
    #     """
    #     time_start = time.time()
    #     res = self.query(query)
    #     print(res)
    #     time_end = time.time()
    #     context, source =  self.format_response(res)

        
    #     return context, source
 
