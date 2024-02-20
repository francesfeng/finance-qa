import json
import sys
from loguru import logger

class Config:
    """Config class for the app"""

    def __init__(self, config_path: str = None):
        # Initialise the config class
        self.config_path = config_path
        self.config = self.load_config()
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)" \
                          " Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
        
        self.logging_path = 'sys.log'

        self.max_search_results_per_query = 5
        self.chunking_size = 350
        self.max_num_chunks = 100
        self.min_chunk_char = 25
        self.similarity_threshold = 0.78

        self.query_similarity_threshold = 0.92 #search query cache based on user's query

        self.model_base = 'gpt-3.5-turbo-1106'
        self.model_advanced = 'gpt-4-1106-preview'
        self.model_embed = 'text-embedding-3-small'



        self.load_config()
        #logger.add(self.logging_path, rotation="500 MB")
        #logger.add(sys.stderr)


    def load_config(self):
        """Load the config file"""
        if self.config_path is None:
            return None
        
        with open(self.config_path, "r") as f:
            config = json.load(f)

        for k, v in config.items():
            self.__dict__[k] = v
