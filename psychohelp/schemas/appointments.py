from datetime import datetime

from pydantic import BaseModel

from psychohelp.repositories.appointments import (
    UUID,
    AppointmentStatus,
    AppointmentType,
)


class AppointmentBase(BaseModel):
    id: UUID
    patient_id: UUID
    therapist_id: UUID
    type: AppointmentType
    reason: str | None = None
    status: AppointmentStatus
    remind_time: datetime | None = None
    last_change_time: datetime
    venue: str

    class Config:
        from_attributes = True


class AppointmentCreateRequest(BaseModel):
    patient_id: UUID
    therapist_id: UUID
    type: AppointmentType
    reason: str | None = None
    remind_time: datetime | None = None
    venue: str | None = None
