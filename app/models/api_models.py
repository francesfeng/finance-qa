from pydantic import BaseModel
from typing import List, Optional, Dict 
from enum import Enum
from app.models.models import ResponseType


class Label(str, Enum):
    text = "text"
    database = "database"


# Define the model. TODO: move to seperate models.api file
class QueryText(BaseModel):
    query: str
    data: str = None

class RelatedTopic(BaseModel):
    query: str
    title: str
    label: str

class Response(BaseModel):
    code: int
    type: ResponseType
    label: Label
    query: str
    title: Optional[str] = None
    response: Optional[str] = None
    related_topics: Optional[List[Dict[str, str]]] = None
