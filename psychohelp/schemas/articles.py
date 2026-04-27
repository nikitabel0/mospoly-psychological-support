from uuid import UUID

from pydantic import BaseModel, Field


class ArticleCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    text: str = Field(..., min_length=1)


class ArticleUpdateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    text: str = Field(..., min_length=1)


class ArticleResponse(BaseModel):
    id: UUID
    title: str
    text: str

    class Config:
        from_attributes = True
