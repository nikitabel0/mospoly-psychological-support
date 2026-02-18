# psychohelp/schemas/applications.py

from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from enum import Enum
from typing import Optional


class UniversityStatus(str, Enum):
    STUDENT = "студент"
    POSTGRADUATE = "аспирант"
    TEACHER = "преподаватель"
    STAFF = "сотрудник"


class ApplicationStatus(str, Enum):
    NEW = "новая"
    IN_PROGRESS = "в обработке"
    COMPLETED = "завершена"
    REJECTED = "отклонена"


class ApplicationCreateRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    problem_description: str = Field(..., min_length=10, max_length=2000)
    preferred_campus: str = Field(..., min_length=1, max_length=128)
    university_status: UniversityStatus


class ApplicationUpdateRequest(BaseModel):
    status: Optional[ApplicationStatus] = None


class ApplicationResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    first_name: str
    last_name: str
    email: str
    phone: str
    problem_description: str
    preferred_campus: str
    university_status: UniversityStatus
    status: ApplicationStatus
    created_at: datetime
    updated_at: datetime
    appointment_id: Optional[UUID]

    class Config:
        from_attributes = True
        use_enum_values = True