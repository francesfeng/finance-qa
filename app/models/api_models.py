from pydantic import BaseModel
from typing import List, Optional, Dict 
from enum import Enum


class Label(str, Enum):
    text = "text"
    database = "database"

class QueryText(BaseModel):
    query: Optional[str] = None
    data: Optional[str] = None


class RelatedTopic(BaseModel):
    query: str
    title: str
    label: str

class Response(BaseModel):
    code: int
    label: Optional[Label] = None
    query: Optional[str] = None
    title: Optional[str] = None
    related_topics: Optional[List[Dict[str, str]]] = None


class Query(BaseModel):
    query: str
   

class QueryThread(BaseModel):
    assistant_id: str
    thread_id: str
    query: str

class MessageResponse(BaseModel):
    role: str
    content: str


class MessageFileResponse(MessageResponse):
    image_files: Optional[List[str]] = None


