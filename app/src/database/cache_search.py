import asyncpg
from typing import List
from datetime import datetime
from loguru import logger

from app.models.models import DocumentSearch
from .backend_db import BackendDB

#level_db = logger.level("CACHE", no=38, color="<yellow>", icon="♣")

class SearchCache(BackendDB):

    def __init__(self):
        super().__init__()
        self.conn = None

    async def create_connection(self):
        self.conn = await super().create_connection()

    
    async def close(self):
        if self.conn:
            await self.conn.close()


    async def insert_searches(self, docs: List[DocumentSearch]):
        """"
            Insert search result to the search cache 
            It allows duplicaations, as highest number of duplication indicates importance
        """
        try:
            await self.create_connection()
            async with self.conn.transaction():
                for doc in docs:
                    url = doc.metadata.url
                    if url.endswith('.pdf'):
                        type = 'PDF'
                    elif 'arxiv.org/' in url:
                        type = 'Academic paper'
                    elif 'youtube.com' in url:
                        type = 'video'
                    else:
                        type = 'HTML'
                    
                    sql_query = """
                        INSERT INTO search_cache (query, url, type, publisher, author, title, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        ON CONFLICT (query, url) do nothing
                        """
                    
                    created_at = datetime.strptime(doc.metadata.created_at, '%Y-%m-%d') if doc.metadata.created_at else None
                    current = datetime.utcnow()
                    await self.conn.execute(sql_query, doc.query, 
                                        doc.metadata.url, 
                                        type, 
                                        doc.metadata.publisher, 
                                        doc.metadata.author, 
                                        doc.metadata.title, 
                                        created_at,
                                        current,
                                        )
                logger.opt(lazy=True).log("CACHE", f"Search Cache Insert | Inserted {len(docs)} searches to the database")
        except Exception as e:
            logger.error(f"Insert the search results | Error in inserting search results in search_Cache: {e}")
        finally:
            await self.conn.close()
        return
    
    
    
     
        
    async def update_scrape_status(self):
        """
            Check if the url has been succesfully scraped
            If so, update the is_scrapped to True
        """

        sql_query = """
            UPDATE search_cache
            SET is_scraped = scrapped.is_scrapped
            FROM (
                SELECT
                    t1.url,
                    CASE
                        WHEN t2.url IS NOT NULL THEN TRUE
                        ELSE FALSE
                    END as is_scrapped
                FROM
                    search_cache t1
                LEFT JOIN
                    (SELECT DISTINCT url FROM embeddings) t2 ON t1.url = t2.url
            ) AS scrapped
            WHERE search_cache.url = scrapped.url;
            """
        
        try:
            await self.create_connection()
            await self.conn.execute(sql_query)

        except Exception as e:
            logger.error(f"Update scrape results | Error updating scrape results in search_Cache: {e}")

        return 
        

                    
            



