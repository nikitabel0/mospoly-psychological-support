from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class ReviewsBase(BaseModel):
    appointment_id: UUID
    time: datetime
    content: str
    
    class Config:
        from_attributes = True


class ReviewCreateRequest(BaseModel):
    appointment_id: UUID = Field(..., description="ID записи на прием")
    content: str = Field(..., min_length=1, max_length=5000, description="Текст отзыва")
