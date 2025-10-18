from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber

from uuid import UUID


PhoneNumber.phone_format = "E164"
PhoneNumber.default_region_code = "+7"


class UserCreateRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    middle_name: str | None = Field(None, min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    phone_number: PhoneNumber
    email: EmailStr | None = None
    social_media: str | None = Field(None, max_length=50)
    password: str = Field(min_length=8, max_length=256)


class UserBase(BaseModel):
    id: UUID
    first_name: str = Field(min_length=1, max_length=50)
    middle_name: str | None = Field(None, min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    phone_number: PhoneNumber
    email: EmailStr | None = None
    social_media: str | None = Field(None, max_length=50)
    password: str


class UserResponse(BaseModel):
    id: UUID
    first_name: str = Field(min_length=1, max_length=50)
    middle_name: str | None = Field(None, min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    phone_number: PhoneNumber
    email: EmailStr | None = None
    social_media: str | None = Field(None, max_length=50)

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    status_code: int
    access_token: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
