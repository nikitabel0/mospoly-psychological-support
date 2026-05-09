import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from psychohelp.config.config import Base


class AppointmentRescheduleStatus(enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    rejected = "rejected"


class AppointmentRescheduleRequest(Base):
    __tablename__ = "appointment_reschedule_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    appointment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("appointments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    requested_by_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status = Column(
        Enum(AppointmentRescheduleStatus),
        nullable=False,
        default=AppointmentRescheduleStatus.pending,
        index=True,
    )

    old_scheduled_time = Column(DateTime(timezone=True), nullable=False)
    old_remind_time = Column(DateTime(timezone=True), nullable=True)
    old_venue = Column(String(128), nullable=False)
    old_comment = Column(String(512), nullable=True)

    requested_scheduled_time = Column(DateTime(timezone=True), nullable=False)
    requested_remind_time = Column(DateTime(timezone=True), nullable=True)
    requested_venue = Column(String(128), nullable=True)
    requested_comment = Column(String(512), nullable=True)

    rejection_comment = Column(String(512), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    responded_at = Column(DateTime(timezone=True), nullable=True)

    appointment = relationship("Appointment", back_populates="reschedule_requests")
    requested_by = relationship("User")
