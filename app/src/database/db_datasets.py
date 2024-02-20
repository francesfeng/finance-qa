import asyncpg
import sqlalchemy
import os
from io import StringIO
import csv
import pandas as pd
from datetime import datetime
import json
import asyncio
from typing import List, Dict, Any, Optional
from app.models.models import DocumentChunk, DocumentChunkMetadata, DocumentSearch, Response
from app.src.utils.hash import text_to_hash
from app.src.connect.gpt_v2 import get_embeddings_v2
from app.src.config.config import Config
from loguru import logger


host = os.environ['NEON_HOST']
user = os.environ['NEON_USER']
password = os.environ['NEON_PASSWORD']
database = 'datasets'

assert host is not None
assert database is not None
assert user is not None
assert password is not None

level_db = logger.level("BACKENDDATABASE", no=38, color="<yellow>", icon="♣")

class DatasetsDB:

    def __init__(self, config_path: Optional[str] = None):
        config = Config(config_path)
        self.model_embed = config.model_embed
        return
    

    async def create_connection(self):
        self.conn = await asyncpg.connect(host=host, database=database, user=user, password=password)
        

    async def close(self):
        await self.conn.close()


    async def insert_record(self, assistant_id: str, thread_id: str):
        """
            Insert a new record to the data_requests table. 
        """
        # Establish database connection
        await self.create_connection()
        
        # Set fields
        created_at = datetime.utcnow()
        updated_at = datetime.utcnow()
        status = 'added'

        # Insert query
        query = "INSERT INTO data_requests(thread_id, assistant_id, created_at, updated_at, status) VALUES ($1, $2, $3, $4, $5)"
        try: 
            # Insert a record when an assistant is created
            await self.conn.execute(query, thread_id, assistant_id, created_at, updated_at, status)
            print("Record inserted successfully")
            return True
        except Exception as e:
            print(f"Error inserting record: {e}")
            return False
        

    async def insert_record_analysis(self, assistant_id: str, thread_id: str, dataset_name: str):
        """
            Insert a new record to the analysis_requests table. 
        """

        await self.create_connection()
        
        # Set fields
        created_at = datetime.utcnow()
        updated_at = datetime.utcnow()
        status = 'added'

        query = "INSERT INTO analysis_requests (thread_id, assistant_id, dataset_name, created_at, updated_at) VALUES ($1, $2, $3, $4, $5)"
        try: 
            await self.conn.execute(query, thread_id, assistant_id, dataset_name, created_at, updated_at)
        except Exception as e:
            print(f"Error inserting record: {e}")
        return

    
    async def get_messages_by_thread_id(self, table_name: str, thread_id: str):
        await self.create_connection()
        try: 

            # Retrieve messages based on thread_id
            query = f"SELECT messages FROM {table_name} WHERE thread_id = $1"
            row = await self.conn.fetchrow(query, thread_id)

            if row is not None:
                return json.loads(row.get('messages'))
        except Exception as e:
            print(e)
        return
            


    async def update_message(self, table_name: str, thread_id: str, messages: List[Dict[str, Any]]):
            """
            Update the messages for a given thread_id in the database.

            Args:
                thread_id (int): The primary key of the record to be updated.
                messages (list): The new messages to be added to the existing messages.

            Returns:
                bool: True if the record is updated successfully, False otherwise.
            """

            # retrieve messages by thread_id
            current_messages = await self.get_messages_by_thread_id(table_name, thread_id)
            
            # pending new messages
            if current_messages:
                current_messages.extend(messages)
            else:
                current_messages = messages

            await self.create_connection()
            try: 

                # update the updated_at field
                updated_at = datetime.utcnow()

                # Insert new messages, query, updated_at to the database
                update_query = f"UPDATE {table_name} SET messages = $1, updated_at = $2 WHERE thread_id = $3"
                await self.conn.execute(update_query ,json.dumps(current_messages), updated_at, thread_id)

            except Exception as e:
                print(f"Error updating messages for thread_id: {thread_id}: {e}")
                return False
            
            
    async def update_user_query(self, thread_id: str, query: str):
        """
            Insert the first user query to data_requests table
        """
        await self.create_connection()

        try:
            update_user_query = "UPDATE data_requests SET user_query = CASE WHEN thread_id = $1 AND user_query IS NULL THEN $2 ELSE user_query END WHERE thread_id = $1"
            await self.conn.execute(update_user_query, thread_id, query)

        except Exception as e:
            print(f"Error updating messages for thread_id: {thread_id}: {e}")
        
        return
    
    async def insert_image(self, file_id: str, bytes_data: bytes):
        """
            Insert image's file_id and bytes data to image_files table
        """

        await self.create_connection()
        
        # Set fields
        created_at = datetime.utcnow()

        query = "INSERT INTO image_files (file_id, image_bytes, created_at) VALUES ($1, $2, $3)"
        try: 
            await self.conn.execute(query, file_id, bytes_data, created_at)
        except Exception as e:
            print(f"Error inserting record: {e}")
        return
    

    async def get_image_bytes(self, file_id: str):
        """
            Retrieve image bytes data by file_id
        """
        await self.create_connection()
        try: 
            query = "SELECT image_bytes FROM image_files WHERE file_id = $1 LIMIT 1"
            row = await self.conn.fetchrow(query, file_id)
            if row is not None:
                return row.get('image_bytes')
        except Exception as e:
            print(e)
        return
    

    