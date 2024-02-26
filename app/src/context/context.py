from typing import List, Optional
from concurrent.futures.thread import ThreadPoolExecutor
import time
from loguru import logger
from functools import partial


from app.src.config.config import Config
from app.src.utils.chunking import chunking
from app.src.connect.gpt_v2 import get_embeddings_v2
from app.src.utils.similarity import cosine_similarity
from app.models.models import DocumentChunk, DocumentChunkWithScore, DocumentChunkMetadata, DocumentSearch

level_context = logger.level("CONTEXT", no=38, color="<yellow>", icon="♣")


class Context:

    def __init__(self,config_path: Optional[str] = None):
        config = Config(config_path)
        self.chunking_size = config.chunking_size
        #self.query = query
        self.max_num_chunks = config.max_num_chunks
        self.min_chunk_char = config.min_chunk_char
        self.similarity_threshold = config.similarity_threshold
        self.model_embed = config.model_embed
        self.embedding_dimension = config.embedding_dimension




    def get_chunks(self, docs: List[DocumentSearch]) -> List[DocumentSearch]:
        """
        Takes in a list of text and returns a list of chunks, using concurrent
        """
        
        chunks_list = []

        # chunking the list of text, using concurrent
        time_start = time.time()

        chunks_list = [chunk for doc in docs for chunk in self.get_doc_chunks(doc)]

        time_end = time.time()

        logger.opt(lazy=True).log("CONTEXT", f"Chunking | Process time: {time_end - time_start} seconds | Number of documents: {len(docs)} | Number of chunks: {len(chunks_list)}")


        chunks_emb = self.create_embedding(chunks_list)
        return chunks_emb
    
    

    def get_doc_chunks(self, doc: DocumentSearch) -> List[DocumentSearch]:
        """
        Take a sinle document, and return a list of chunks
        """
        # chunk the text
        chunks = chunking(doc.text, 
                          chunk_size=self.chunking_size, 
                          max_num_chunks=self.max_num_chunks, 
                          min_chunk_char=self.min_chunk_char
                          )
        chunks_all = []
        for i, chunk in enumerate(chunks):
            doc_chunk = DocumentSearch(
                id=f"{doc.id}_{i}",
                text=chunk,
                metadata=DocumentChunkMetadata(**doc.metadata.dict()),
                query=doc.query
            )
            doc_chunk.metadata.document_id = doc.id
            chunks_all.append(doc_chunk)

        return chunks_all
    

    def create_embedding(self, docs: List[DocumentSearch]) -> List[DocumentSearch]:
        """
            Create embedding for the chunks
        """
        chunks = docs.copy()
        text = [chunk.text for chunk in chunks]

        embeddings = get_embeddings_v2(text, self.model_embed, self.embedding_dimension)

        # add embedding to the chunk
        for chunk, emb in zip(chunks, embeddings):
            chunk.embedding = emb

        return chunks



    def semantic_search(self, docs: List[DocumentSearch] = None) -> List[List[float]]:
        """
        Takes in a list of text, return a list of chunks with similarity score above threshold
        """
        # Get embeddings for queries
        queries = list(set([doc.query for doc in docs]))
        queries_emb = get_embeddings_v2(queries, self.model_embed, self.embedding_dimension)

        # Create a dictionary of queries and their embeddings
        queries_emb_dict = {query: emb for query, emb in zip(queries, queries_emb)}

        # Calculate similarity score
        chunks_all = []
        time_start = time.time()
        for doc in docs:
            score = cosine_similarity(queries_emb_dict[doc.query], doc.embedding)
            chunk_score = DocumentChunkWithScore(**doc.dict(), score=score)
            chunks_all.append(chunk_score)
        time_end = time.time()
        logger.opt(lazy=True).log("CONTEXT", f"Semantic Search | Number of Documents: {len(docs)} | Process time: {time_end - time_start} seconds")

        
        sorted_chunk = [chunk for chunk in chunks_all if chunk.score > self.similarity_threshold]
        return sorted(sorted_chunk, key=lambda x: x.score, reverse=True)







    

        
