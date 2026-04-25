from psychohelp.repositories.appointments import (
    AppointmentType,
    AppointmentStatus,
    UUID,
)

from pydantic import BaseModel

from datetime import datetime


class AppointmentBase(BaseModel):
    id: UUID
    patient_id: UUID
    patient_first_name: str
    patient_last_name: str
    psychologist_id: UUID
    type: AppointmentType
    reason: str | None = None
    status: AppointmentStatus
    scheduled_time: datetime
    remind_time: datetime | None = None
    last_change_time: datetime
    venue: str
    comment: str | None = None

    class Config:
        from_attributes = True


class AppointmentCreateRequest(BaseModel):
    application_id: UUID | None = None
    patient_id: UUID
    psychologist_id: UUID
    type: AppointmentType
    scheduled_time: datetime
    reason: str | None = None
    remind_time: datetime | None = None
    venue: str | None = None
    comment: str | None = None

class AppointmentCancelRequest(BaseModel):
    cancel_reason: str

class AppointmentDoneRequest(BaseModel):
    conclusion: str
