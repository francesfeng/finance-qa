import os
import pinecone
import logging

# Read environment variables for Pinecone configuration
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.environ.get("PINECONE_ENVIRONMENT")
PINECONE_INDEX = os.environ.get("PINECONE_INDEX")
assert PINECONE_API_KEY is not None
assert PINECONE_ENVIRONMENT is not None
assert PINECONE_INDEX is not None


class DataStore:
    # initialise datastore
    def __init__(self, datastore_api_key, datastore_env, index_name, top_k):
        pinecone.init(api_key=PINECONE_API_KEY,
              environment=PINECONE_ENVIRONMENT)
        self.index = pinecone.Index(PINECONE_INDEX)
        self.top_k = top_k
        

    async def query(self, query):
        # semantic search based on the embeddings of the query
        response = self.index.query(query, top_k=self.top_k, include_metadata = True)
        
        # concatenate the top k text into a
        results = ''
        for text in response['matches']:
            results += text['metadata']['text']+'\n'
        return results

