from typing import List, Optional
from concurrent.futures.thread import ThreadPoolExecutor
import time
from loguru import logger
from functools import partial


from app.src.config.config import Config
from app.src.utils.chunking import chunking
from app.src.connect.gpt_v2 import get_embeddings_v2
from app.src.utils.similarity import similarity
from app.models.models import DocumentChunk, DocumentChunkWithScore, DocumentChunkMetadata

level_context = logger.level("CONTEXT", no=38, color="<yellow>", icon="♣")


class Context:

    def __init__(self, query: str, docs: List[DocumentChunk], config_path: Optional[str] = None):
        config = Config(config_path)
        self.chunking_size = config.chunking_size
        self.query = query
        self.max_num_chunks = config.max_num_chunks
        self.min_chunk_char = config.min_chunk_char
        self.similarity_threshold = config.similarity_threshold

        # chunk the text
        self.chunks = self.get_chunks(docs)


    def get_chunks(self, docs: List[DocumentChunk]) -> List[DocumentChunk]:
        """
        Takes in a list of text and returns a list of chunks, using concurrent
        """
        
        chunks_list = []

        # chunking the list of text, using concurrent
        time_start = time.time()
        with ThreadPoolExecutor() as executor:
            chunks = executor.map(self.get_doc_chunks, docs)
        
        chunks_list = [item for chunk in chunks for item in chunk]
        time_end = time.time()

        logger.opt(lazy=True).log("CONTEXT", f"Chunking | Query: {self.query} | Process time: {time_end - time_start} seconds | Number of text: {len(docs)} | Number of chunks: {len(chunks_list)}")
    

        return chunks_list
    

    def get_doc_chunks(self, doc: DocumentChunk) -> List[DocumentChunk]:
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
            doc_chunk = DocumentChunk(
                id=f"{doc.id}_{i}",
                text=chunk,
                metadata=DocumentChunkMetadata(**doc.metadata.dict())
            )
            doc_chunk.metadata.document_id = doc.id
            chunks_all.append(doc_chunk)

        return chunks_all
    

    def semantic_search(self, text: Optional[List[DocumentChunk]] = None) -> List[List[float]]:
        """
        Takes in a list of text, return a list of chunks with similarity score above threshold
        """
        # Get embeddings for query and the context (after chunking)
        chunks = self.chunks or text
        text = [chunk.text for chunk in chunks]
        emb_query = get_embeddings_v2([self.query])
        emb = get_embeddings_v2(text)

        # Calculate similarity score
        time_start = time.time()
        scores = similarity(emb_query, emb)
        time_end = time.time()
        
        logger.opt(lazy=True).log("CONTEXT", f"Semantic Search | Query: {self.query} | Process time: {time_end - time_start} seconds | Number of similarity conparison: {len(chunks)}")

        # Keep only chunks with similarity score above threshold
        chunks_all = []
        for chunk, score in zip(chunks, scores):
            chunk_score = DocumentChunkWithScore(**chunk.dict(), score=score)
            chunks_all.append(chunk_score)

        sorted_chunk = [chunk for chunk in chunks_all if chunk.score > self.similarity_threshold]
        return sorted_chunk






    

        
