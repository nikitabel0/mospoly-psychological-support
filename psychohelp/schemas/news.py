from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from psychohelp.models.news import NewsType


class NewsCreateRequest(BaseModel):
    slug: str = Field(..., min_length=1, max_length=255)
    image: Optional[str] = None
    type: Optional[NewsType] = None
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    link: Optional[str] = None
    text: Optional[str] = None
    event_date: datetime


class NewsUpdateRequest(BaseModel):
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    image: Optional[str] = None
    type: Optional[NewsType] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    link: Optional[str] = None
    text: Optional[str] = None
    event_date: Optional[datetime] = None


class NewsResponse(BaseModel):
    id: UUID
    slug: str
    image: Optional[str]
    type: Optional[NewsType]
    date: datetime
    event_date: datetime
    title: str
    description: Optional[str]
    link: Optional[str]
    text: Optional[str]

    class Config:
        from_attributes = True