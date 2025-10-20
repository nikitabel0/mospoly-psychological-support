from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from psychohelp.config.database import Base


class Therapist(Base):
    __tablename__ = "therapists"

    id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    experience = Column(String(64), nullable=False)
    qualification = Column(String(128), nullable=False)
    consult_areas = Column(String(128), nullable=False)
    description = Column(String(256), nullable=False)
    office = Column(String(128), nullable=False)
    education = Column(String(127), nullable=False)
    short_description = Column(String(2047), nullable=False)
    photo = Column(String(127), nullable=True)

    user = relationship("User", back_populates="therapist_info")
