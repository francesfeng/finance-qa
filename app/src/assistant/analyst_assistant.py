# Higher level exeuction class for conversations assistant thread
# Use to process user's request for data collection & extraction
import asyncio
from io import StringIO
import pandas as pd
from datetime import datetime
import yaml
import os

from typing import List, Dict
from .assistants import create_assistant, submit_query, upload_file, add_message_to_thread
from app.src.database.db import Database
from app.src.database.db_datasets import DatasetsDB
from app.models.models import AssistantModel
from app.src.utils.date import get_utcnow
from app.src.connect.gpt_v2 import get_image

from app.src.config.config import Config


class AnalystAssistant:

    def __init__(self, model: str = 'advanced', config_path: str=None):
        self.db = Database()
        self.db_datasets = DatasetsDB()

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


    
    async def create_assistant(self, dataset: str) -> AssistantModel:
        """
        Initialize a new conversation thread with data assistant
        """

        
        files = os.listdir('temp/')

        # If dataset is not saved in csv yet, retrieve all data and save in csv
        if f'{dataset}.csv' not in files:
            # Retrieve all data from a datatable
            sql = f"SELECT * FROM {dataset}"
            data = self.db.execute_query(sql)
        
            # Name for the csv file, table name + timestamp
            #timestamp = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S')
            file_path = f"temp/{dataset}.csv"

            # Write the data into a temp csv file
            pd.read_csv(StringIO(data)).to_csv(file_path, index=False)

        # Upload the file to file object
        file_obj = upload_file(f"temp/{dataset}.csv")

        assistant = create_assistant('data_analyst', 
                                     self.model, 
                                     code_interpreter=True,
                                     file_obj=file_obj
                                     )

        
        # Load data structure if available
        # TODO: test if this helps with the performance
        structure = self.load_table_structure(dataset)


        
        await self.db_datasets.insert_record_analysis(assistant.assistant_id, assistant.thread_id, dataset)

        return assistant
    

    async def submit_query(self, assistant_id: str, thread_id: str, query: str) -> List[Dict[str, str]]:
        """
        Add new message to a thread, run the thread and return the response
        
        """

        # get the assistant's response
        asst_messages = submit_query(assistant_id=assistant_id, 
                                     thread_id=thread_id, 
                                     query=query, 
                                     use_code_interpreter=True
                                     )
        # add user query to the messages
        messages = [{"role": "user", "content": query, "created_at": get_utcnow()}, 
                    *asst_messages]
        
        # Insert messages to database
        await self.db_datasets.update_message("analysis_requests", thread_id, messages)

        # Get all file_ids from the messages
        file_ids = []
        for m in asst_messages:
            if "image_files" in m and len(m["image_files"]) > 0:
                file_ids.extend(m["image_files"])

        if len(file_ids) > 0:
            for file_id in file_ids:
                # get bytes data from openai
                image_data = await get_image(file_id)

                # store bytes data to database
                await self.db_datasets.insert_image(file_id, image_data)

        return asst_messages
    

    def load_table_structure(self, dataset: str):
        """
        Load details of a dataset from yaml file
        """
        with open("app/src/config/datasets.yaml") as f:
            datasets = yaml.load(f, Loader=yaml.FullLoader)
            if "structure" in datasets[dataset]:
                structure = datasets[dataset]["structure"]
                if len(structure) > 0:
                    return structure
            
            return None
        
