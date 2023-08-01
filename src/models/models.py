from typing import Optional, List
from pydantic import BaseModel

from enum import Enum


class PromptType(str, Enum):
    table_datastore = "table_datastore"
    text = "text"
    sql = "sql"

    table_to_chart = "table_to_chart"
    sqldata_to_chart = "sqldata_to_chart"

    title_and_related = "title_and_related"
    verify = "verify"
    


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






