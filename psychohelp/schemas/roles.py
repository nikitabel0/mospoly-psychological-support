from pydantic import BaseModel

from psychohelp.constants.rbac import RoleCode


class RoleResponse(BaseModel):
    code: str
    name: str
    description: str | None

    class Config:
        from_attributes = True


class RoleAssignRequest(BaseModel):
    role_code: RoleCode


class RoleRemoveRequest(BaseModel):
    role_code: RoleCode
