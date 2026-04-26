from psychohelp.repositories.appointments import (
    AppointmentType,
    AppointmentStatus,
    UUID,
)
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# --- Полные схемы для вложенных объектов ---

class UserFullResponse(BaseModel):
    id: UUID
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    phone_number: str
    email: EmailStr
    social_media: Optional[str] = None
    study_group: Optional[str] = None
    # Пароль намеренно исключен

    class Config:
        from_attributes = True


class PsychologistFullResponse(BaseModel):
    id: UUID
    user_id: UUID
    experience: str
    qualification: str
    consult_areas: str
    description: str
    office: str
    education: str
    short_description: str
    photo: Optional[str] = None
    # Вложенный профиль пользователя для психолога
    user: UserFullResponse 

    class Config:
        from_attributes = True


# --- Основные схемы ---

class AppointmentBase(BaseModel):
    id: UUID
    
    # Полные вложенные объекты вместо UUID
    patient: UserFullResponse
    psychologist: PsychologistFullResponse
    
    application_id: Optional[UUID] = None
    type: AppointmentType
    reason: Optional[str] = None
    status: AppointmentStatus
    scheduled_time: datetime
    remind_time: Optional[datetime] = None
    last_change_time: datetime
    venue: str
    comment: Optional[str] = None
    cancel_reason: Optional[str] = None
    conclusion: Optional[str] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class AppointmentCreateRequest(BaseModel):
    application_id: Optional[UUID] = None
    patient_id: UUID
    psychologist_id: UUID
    type: AppointmentType
    scheduled_time: datetime
    reason: Optional[str] = None
    remind_time: Optional[datetime] = None
    venue: Optional[str] = None
    comment: Optional[str] = None


class AppointmentCancelRequest(BaseModel):
    cancel_reason: str


class AppointmentDoneRequest(BaseModel):
    conclusion: str