import uuid

from sqlalchemy import Column, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from psychohelp.config.database import Base
from psychohelp.constants.rbac import PermissionCode


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    code = Column(
        SQLEnum(PermissionCode, name="permissioncode", native_enum=True),
        unique=True,
        nullable=False,
        index=True,
    )
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    resource = Column(String(50), nullable=False, index=True)

    roles = relationship("Role", secondary="roles_permissions", back_populates="permissions")
