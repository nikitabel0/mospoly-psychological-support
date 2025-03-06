from pydantic import BaseModel
from uuid import UUID

class TherapistBase(BaseModel):
    id: UUID
    first_name: str
    middle_name: str | None
    last_name: str
    phone_number: str
    experience: str
    qualification: str
    consult_areas: str
    description: str
    office: str
    education: str
    short_description: str
    photo: str

    class Config:
        orm_mode = True
