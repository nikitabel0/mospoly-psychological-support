from psychohelp.config.config import Base

from sqlalchemy import Column, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


class Review(Base):
    __tablename__ = "reviews"

    appointment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("appointments.id", ondelete="CASCADE"),
        primary_key=True,
    )
    time = Column(DateTime, nullable=False)
    content = Column(Text, nullable=False)

    appointment = relationship("Appointment", back_populates="review")
