from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber
from typing import Optional
from psychohelp.schemas.roles import RoleResponse 
from uuid import UUID


PhoneNumber.phone_format = "E164"
PhoneNumber.default_region_code = "+7"


class UserCreateRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    middle_name: str | None = Field(None, min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    phone_number: PhoneNumber
    email: EmailStr
    social_media: str | None = Field(None, max_length=50)
    password: str = Field(min_length=8, max_length=256)
    study_group: Optional[str] = Field(None, max_length=50)


class UserBase(BaseModel):
    id: UUID
    first_name: str = Field(min_length=1, max_length=50)
    middle_name: str | None = Field(None, min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    phone_number: PhoneNumber
    email: EmailStr
    social_media: str | None = Field(None, max_length=50)
    password: str


class UserResponse(BaseModel):
    id: UUID
    first_name: str = Field(min_length=1, max_length=50)
    middle_name: str | None = Field(None, min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    phone_number: PhoneNumber
    email: EmailStr
    social_media: str | None = Field(None, max_length=50)
    roles: list[RoleResponse] = []
    study_group: Optional[str] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    status_code: int
    access_token: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)


class UserUpdateRequest(BaseModel):
    """Схема для обновления профиля (все поля опциональны)"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    middle_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone_number: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    social_media: Optional[str] = Field(None, max_length=50)
    study_group: Optional[str] = Field(None, max_length=50)


class PasswordChangeRequest(BaseModel):
    """Схема для смены пароля"""
    old_password: str = Field(..., min_length=8, max_length=64)
    new_password: str = Field(..., min_length=8, max_length=64)