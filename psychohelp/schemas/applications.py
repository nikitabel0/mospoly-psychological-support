from pydantic import BaseModel, EmailStr, Field, field_validator
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
    NEW = "new"
    IN_PROGRESS = "in_progress"
    AWAITING_USER_CONFIRMATION = "awaiting_user_confirmation"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class CancelInitiator(str, Enum):
    USER = "user"
    PSYCHOLOGIST = "psychologist"
    MANAGER = "manager"
    SYSTEM = "system"


class MeetingType(str, Enum):
    OFFLINE = "offline"
    ONLINE = "online"


class ApplicationCreateRequest(BaseModel):
    psychologist_id: UUID
    scheduled_at: datetime
    problem_description: str = Field(..., min_length=10, max_length=2000)
    preferred_campus: Optional[str] = Field(None, max_length=128)
    university_status: UniversityStatus


class AcceptToProcessingRequest(BaseModel):
    assigned_to: UUID


class OfferConsultationRequest(BaseModel):
    psychologist_id: UUID
    meeting_type: MeetingType
    scheduled_at: datetime
    location_address: Optional[str] = None
    meeting_url: Optional[str] = None

    @field_validator('scheduled_at')
    def validate_scheduled_at(cls, v):
        if v <= datetime.now(v.tzinfo):
            raise ValueError('Дата и время встречи не могут быть в прошлом')
        return v


class RejectRequest(BaseModel):
    reject_reason: str = Field(..., min_length=1, max_length=500)


class CancelRequest(BaseModel):
    cancel_reason: str = Field(..., min_length=1, max_length=500)
    cancel_initiator: CancelInitiator


class ApplicationResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    first_name: str
    last_name: str
    email: str
    phone: str
    problem_description: str
    preferred_campus: Optional[str]
    university_status: UniversityStatus
    status: ApplicationStatus
    assigned_to: Optional[UUID]
    psychologist_id: Optional[UUID]
    meeting_type: Optional[MeetingType]
    scheduled_at: Optional[datetime]
    location_address: Optional[str]
    meeting_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    processing_started_at: Optional[datetime]
    confirmation_requested_at: Optional[datetime]
    completed_at: Optional[datetime]
    rejected_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    expired_at: Optional[datetime]
    reject_reason: Optional[str]
    cancel_reason: Optional[str]
    cancel_initiator: Optional[CancelInitiator]
    internal_comment: Optional[str]
    appointment_id: Optional[UUID]
    version: int

    class Config:
        from_attributes = True
        use_enum_values = True