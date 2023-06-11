import os
import pinecone
import logging

class DataStore:
    # initialise datastore
    def __init__(self, datastore_api_key, datastore_env, index_name, top_k):
        pinecone.init(api_key=datastore_api_key,
              environment=datastore_env)
        self.index = pinecone.Index(index_name)
        self.top_k = top_k
        

    def query(self, query):
        # semantic search based on the embeddings of the query
        response = self.index.query(query, top_k=self.top_k, include_metadata = True)
        
        # concatenate the top k text into a
        results = ''
        for text in response['matches']:
            results += text['metadata']['text']+'\n'
        return results

