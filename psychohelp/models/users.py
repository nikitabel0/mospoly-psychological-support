import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from psychohelp.config.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=False)
    phone_number = Column(String(20), nullable=False)
    email = Column(String(64), unique=True)
    social_media = Column(String(50), nullable=True)
    password = Column(String(64), nullable=False)

    roles = relationship("Role", back_populates="user")
    appointments_as_patient = relationship(
        "Appointment", foreign_keys="[Appointment.patient_id]", back_populates="patient"
    )
    appointments_as_therapist = relationship(
        "Appointment",
        foreign_keys="[Appointment.therapist_id]",
        back_populates="therapist",
    )
    therapist_info = relationship("Therapist", back_populates="user", uselist=False)
