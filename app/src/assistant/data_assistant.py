# Higher level exeuction class for conversations assistant thread
# Use to process user's request for data collection & extraction
import asyncio
from typing import List, Dict
from .assistants import create_assistant ,submit_query
from app.src.database.db_datasets import DatasetsDB
from app.models.models import AssistantModel

from app.src.config.config import Config
from app.src.utils.date import get_utcnow

class DataAssistant:

    def __init__(self, model: str = 'base', config_path: str=None):
        self.db = DatasetsDB()

        # set config
        config = Config(config_path)
        # set model
        if model == 'base':
            self.model = config.model_base
        elif model == 'advanced':
            self.model = config.model_advanced
        else:
            print('Model not found, using base model instead')
            self.model = config.model_base



    
    async def create_assistant(self) -> AssistantModel:
        """
        Initialize a new conversation thread with data assistant

        """

        # Create a new conversation and return the conversation object
        asst = create_assistant('data_assistant', self.model)

        # Insert the conversation to database
        await self.db.insert_record(asst.assistant_id, asst.thread_id)
        return asst


    async def submit_query(self, 
                           assistant_id: str, 
                           thread_id: str, 
                           query: str
                           ) -> List[Dict[str, str]]:
        """
        Add new message to a thread, run the thread and return the response
        
        """

        # get the assistant's response
        response = submit_query(assistant_id, thread_id, query)

        # create last user and assistant messages

        asst_response = response[-1]

        # Combine user and assistant messages
        messages = [{"role": "user", "content": query, "created_at": get_utcnow()}, 
                    asst_response]

        # Store the messages to database
        await self.db.update_message('data_requests',thread_id, messages)

        # Add user query if it is the first query
        await self.db.update_user_query(thread_id, query)

        return {"role": asst_response["role"], "content": asst_response["content"]}
    


    


