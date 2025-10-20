import enum

from sqlalchemy import Column, Enum, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from psychohelp.config.database import Base


class UserRole(enum.Enum):
    Therapist = "Therapist"
    Administrator = "Administrator"


class Role(Base):
    __tablename__ = "roles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    role = Column(Enum(UserRole), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("user_id", "role"),)
    user = relationship("User", back_populates="roles")
