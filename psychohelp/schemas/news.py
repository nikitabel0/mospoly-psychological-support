from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class NewsCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    text: str = Field(..., min_length=1)


class NewsUpdateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    text: str = Field(..., min_length=1)


class NewsResponse(BaseModel):
    id: UUID
    title: str
    text: str
    created_at: datetime

    class Config:
        from_attributes = True