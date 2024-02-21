import asyncpg 
import os

from typing import Optional

from app.src.config.config import Config

host = os.environ['NEON_HOST']
user = os.environ['NEON_USER']
password = os.environ['NEON_PASSWORD']
database = 'datasets'

assert host is not None
assert database is not None
assert user is not None
assert password is not None

class BackendDB:
    def __init__(self, config_path: Optional[str] = None):
        config = Config(config_path)
        self.model_embed = config.model_embed
        return
    

    async def create_connection(self):
        return await asyncpg.connect(host=host, database=database, user=user, password=password)
        

