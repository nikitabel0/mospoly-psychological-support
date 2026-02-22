from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
import enum

from psychohelp.config.config import Base


class UniversityStatus(enum.Enum):
    STUDENT = "студент"
    POSTGRADUATE = "аспирант"
    TEACHER = "преподаватель"
    STAFF = "сотрудник"


class ApplicationStatus(enum.Enum):
    NEW = "новая"
    IN_PROGRESS = "в обработке"
    COMPLETED = "завершена"
    REJECTED = "отклонена"


class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(64), nullable=False)
    phone = Column(String(20), nullable=False)
    problem_description = Column(Text, nullable=False)         
    preferred_campus = Column(String(128), nullable=False)     
    university_status = Column(String(50), nullable=False)
    status = Column(String(50), default=ApplicationStatus.NEW.value, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", foreign_keys=[user_id])
    appointment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("appointments.id", ondelete="SET NULL"),
        nullable=True
    )
    appointment = relationship("Appointment", foreign_keys=[appointment_id])