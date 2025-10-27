"""
Pydantic схемы для работы с ролями
"""

from pydantic import BaseModel


class RoleResponse(BaseModel):
    """Схема ответа с информацией о роли"""
    code: str
    name: str
    description: str | None

    class Config:
        from_attributes = True


class RoleAssignRequest(BaseModel):
    """Схема запроса на назначение роли"""
    role_code: str


class RoleRemoveRequest(BaseModel):
    """Схема запроса на удаление роли"""
    role_code: str

