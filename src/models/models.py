from typing import Optional, List, Dict
from pydantic import BaseModel

from enum import Enum


class Source(str, Enum):
    press_release = "press_release"
    investor_presentation = "investor_presentation"
    regulatory_filing = "regulatory_filing"

    news_article = "news"
    blog_post = "blog_post"
    social_media = "social_media"

    equity_research = "equity_research"
    industry_report = "industry_report"

    legislation = "legislation"
    
    other = "other"


class Type(str, Enum):
    pdf = "pdf"
    table = "table"
    html = "html"
    text = "text"
    image = "image" # reserved for future chart recognition
    other = "other"




class DocumentMetadata(BaseModel):
    source: Optional[Source] = None
    type: Optional[Type] = None
    publisher: Optional[str] = None
    url: Optional[str] = None
    created_at: Optional[str] = None
    author: Optional[str] = None
    title: Optional[str] = None


class DocumentChunkMetadata(DocumentMetadata):
    document_id: Optional[str] = None

class DocumentChunk(BaseModel):
    id: Optional[str] = None
    text: str
    metadata: DocumentChunkMetadata
    embedding: Optional[List[float]] = None


class DocumentChunkWithScore(DocumentChunk):
    score: float

class DocumentMetadataFilter(BaseModel):
    document_id: Optional[str] = None
    source: Optional[str] = None
    type: Optional[str] = None
    publisher: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    author: Optional[str] = None
    title: Optional[str] = None


class Query(BaseModel):
    query: str
    filter: Optional[DocumentMetadataFilter] = None
    top_k: Optional[int] = None


class QueryWithEmbedding(Query):
    embedding: List[float] 


class ResponseType(str, Enum):
    text = "text" # streaming text from datastore
    table = "table" # streaming table from datastore
    data = "data" # sql data
    chart = "chart" #
    textdata = "textdata" # text from sql data
    error = "error"



class Label(str, Enum):
    text = "text"
    database = "database"


class Response(BaseModel):
    code: int
    type: ResponseType
    label: Label
    query: str
    title: Optional[str] = None
    response: Optional[str] = None
    related_topics: Optional[List[Dict[str, str]]] = None





