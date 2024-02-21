import asyncpg
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from loguru import logger

from app.models.models import DocumentChunk, DocumentChunkMetadata, DocumentSearch, Response
from app.src.utils.hash import text_to_hash
from app.src.connect.gpt_v2 import get_embeddings_v2
from app.src.config.config import Config


host = os.environ['NEON_HOST']
user = os.environ['NEON_USER']
password = os.environ['NEON_PASSWORD']
database = 'datasets'


level_db = logger.level("CACHE", no=38, color="<yellow>", icon="♣")

class EmbeddingCache:
    def __init__(self, config_path: Optional[str] = None):
        config = Config(config_path)
        self.model_embed = config.model_embed
        return
    

    async def create_connection(self):
        self.conn = await asyncpg.connect(host=host, database=database, user=user, password=password)
        

    async def close(self):
        await self.conn.close()


    async def retrieve_embeddings(self, document_ids: List[str]):
        """
            Retrieve embeddings from the database by document_ids
        """

        await self.create_connection()

        ids_str = '(\'' + '\',\''.join(document_ids) + '\')'

        query = f"SELECT * FROM embeddings WHERE document_id IN {ids_str}"
        rows = await self.conn.fetch(query)

        results = [dict(r) for r in rows]
        for r in results:
        
            # convert created_at to string
            r['created_at'] = r['created_at'].strftime('%Y-%m-%d') if r['created_at'] else None

            # convert embedding to list
            emb_list = r['embedding'][1:-1].split(',')
            r['embedding'] = [float(e) for e in emb_list]

        docs = [DocumentSearch(id=r['id'], text=r['text'], embedding=r['embedding'], metadata=DocumentChunkMetadata(**r)) for r in results]
        logger.opt(lazy=True).log("CACHE", f"Embedding Retrieval | Retrieved {len(docs)} embeddings from the database")

        return docs
    

    async def insert_embeddings(self, docs: List[DocumentChunk], chunking_size: int, embedding_model: str, is_updating: bool = False):
        
        """
            Insert embeddings to the database
        """

        await self.create_connection()
        async with self.conn.transaction():

            #stmt = await self.conn.prepare("INSERT INTO embeddings (id, text, embedding, document_id, source, type, publisher, url, created_at, author, title) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)")
            for doc in docs:
                    
                emb = '[' + ','.join(map(str, doc.embedding)) + ']'

                if not is_updating:
                    query = """
                        INSERT INTO embeddings (id, text, embedding, document_id, chunk_seq ,source, type, publisher, url, created_at, author, title, chunk_size, embedding_model) 
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                        ON CONFLICT (id) DO NOTHING
                        """
                else:
                    query = """
                        INSERT INTO embeddings (id, text, embedding, document_id, chunk_seq ,source, type, publisher, url, created_at, author, title, chunk_size, embedding_model) 
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                        ON CONFLICT (id) DO
                        UPDATE SET id=EXCLUDED.id, text=EXCLUDED.text, embedding=EXCLUDED.embedding, document_id=EXCLUDED.document_id, chunk_seq=EXCLUDED.chunk_seq ,source=EXCLUDED.source, 
                        type=EXCLUDED.type, publisher=EXCLUDED.publisher, url=EXCLUDED.url, created_at=EXCLUDED.created_at, author=EXCLUDED.author, title=EXCLUDED.title, 
                        chunk_size=EXCLUDED.chunk_size, embedding_model=EXCLUDED.embedding_model
                        """

                created_at = datetime.strptime(doc.metadata.created_at, '%Y-%m-%d') if doc.metadata.created_at else None
                await self.conn.execute(query, doc.id, 
                                    doc.text, 
                                    emb, 
                                    doc.metadata.document_id, 
                                    int(doc.id.split('_')[-1]),
                                    doc.metadata.source, 
                                    doc.metadata.type, 
                                    doc.metadata.publisher, 
                                    doc.metadata.url, 
                                    created_at,
                                    doc.metadata.author, 
                                    doc.metadata.title,
                                    chunking_size,
                                    embedding_model,
                                    )
                
        logger.opt(lazy=True).log("CACHE", f"Embedding Insert | Inserted {len(docs)} embeddings to the database")

        return
    

    
    

    