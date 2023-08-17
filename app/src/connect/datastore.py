from typing import List, Optional, Dict, Any
import pinecone
import os

from app.models.models import Query, QueryWithEmbedding, DocumentMetadataFilter, DocumentChunkWithScore
from app.src.connect.gpt import get_embeddings
from app.src.utils.date import to_unix_timestamp, to_datestr

# Read environment variables for Pinecone configuration
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.environ.get("PINECONE_ENVIRONMENT")
PINECONE_INDEX = os.environ.get("PINECONE_INDEX")
assert PINECONE_API_KEY is not None
assert PINECONE_ENVIRONMENT is not None
assert PINECONE_INDEX is not None

class DataStore:

    def __init__(self):
        """
        Initialise the datastore.
        """
        pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
        self.index = pinecone.Index(PINECONE_INDEX)


    async def query(self, query: Query):
        """
        Takes in a list of queries and filters and returns a list of query results with matching document chunks and scores.
        """

        # get a list of just the queries from the Query list
        embeddings = get_embeddings([query.query])

        # Hydrate the query list with the embeddings
        queries_with_embeddings = QueryWithEmbedding(**query.dict(), embedding=embeddings[0])

        pinecone_filter = self._get_pinecone_filter(query.filter)

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
        
        query_results: List[DocumentChunkWithScore] = []

        for result in response["matches"]:
            score = result.score
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
                    pinecone_filter["date"] = pinecone_filter.get("date", {})
                    pinecone_filter["date"]["$gte"] = to_unix_timestamp(value)
                elif field == "end_date":
                    pinecone_filter["date"] = pinecone_filter.get("date", {})
                    pinecone_filter["date"]["$lte"] = to_unix_timestamp(value)
                else:
                    pinecone_filter[field] = value

        return pinecone_filter
    

    def format_response(self, response: List[DocumentChunkWithScore]) -> List[str]:
        """
        Takes in the pinecone response, format into created_at ---- text.
        Only keep retrieved text with score > 0.8.
        """
        context = [f"{to_datestr(i.metadata.created_at)}----{i.text}" for i in response if i.score > 0.8]
        source = [i.metadata.publisher for i in response if i.score > 0.8]
        source = list(set(source))
        return context, source


    def combine_sort_retrieval(self, res1: List[DocumentChunkWithScore], res2: List[DocumentChunkWithScore]) -> List[str]:
        """
        Combine the results from two queries and sort by score.
        """
        res = res1 + res2
        res.sort(key=lambda x: x.score, reverse=True)
        return self.format_response(res)
 
