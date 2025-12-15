from psychohelp.config.config import Base

from sqlalchemy import Column, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

import enum
import uuid


class AppointmentType(enum.Enum):
    Offline = "Offline"
    Online = "Online"


class AppointmentStatus(enum.Enum):
    Approved = "Approved"
    Accepted = "Accepted"
    Cancelled = "Cancelled"
    Done = "Done"


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    patient_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    psychologist_id = Column(
        UUID(as_uuid=True), ForeignKey("psychologists.id", ondelete="CASCADE"), nullable=False
    )
    type = Column(Enum(AppointmentType), nullable=False)
    reason = Column(String(64), nullable=True)
    status = Column(Enum(AppointmentStatus), nullable=False)
    scheduled_time = Column(DateTime(timezone=True), nullable=False, comment="Время назначенной встречи")
    remind_time = Column(DateTime(timezone=True), nullable=True, comment="Время напоминания")
    last_change_time = Column(DateTime(timezone=True), nullable=False, comment="Время последнего изменения")
    venue = Column(String(128), nullable=False, comment="Место проведения встречи")
    comment = Column(String(512), nullable=True, comment="Комментарий к записи")

    patient = relationship(
        "User", foreign_keys=[patient_id], back_populates="appointments_as_patient"
    )
    psychologist = relationship(
        "Psychologist", foreign_keys=[psychologist_id], back_populates="appointments"
    )
    review = relationship("Review", back_populates="appointment", uselist=False)
