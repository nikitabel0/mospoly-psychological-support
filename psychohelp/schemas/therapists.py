from uuid import UUID

from pydantic import BaseModel


class TherapistBase(BaseModel):
    """Базовая схема психолога без информации о пользователе"""
    id: UUID
    experience: str
    qualification: str
    consult_areas: str
    description: str
    office: str
    education: str
    short_description: str
    photo: str | None

    class Config:
        from_attributes = True


class TherapistResponse(BaseModel):
    """Схема ответа API с полной информацией о психологе"""
    id: UUID
    experience: str
    qualification: str
    consult_areas: str
    description: str
    office: str
    education: str
    short_description: str
    photo: str | None
    # Данные из связанной модели User
    first_name: str
    middle_name: str | None
    last_name: str
    phone_number: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_therapist(cls, therapist):
        """
        Создание схемы из ORM модели Therapist с данными пользователя
        
        Args:
            therapist: ORM модель Therapist с загруженным relationship user
            
        Returns:
            TherapistResponse: Pydantic схема с данными психолога и пользователя
        """
        return cls(
            id=therapist.id,
            experience=therapist.experience,
            qualification=therapist.qualification,
            consult_areas=therapist.consult_areas,
            description=therapist.description,
            office=therapist.office,
            education=therapist.education,
            short_description=therapist.short_description,
            photo=therapist.photo,
            first_name=therapist.user.first_name,
            middle_name=therapist.user.middle_name,
            last_name=therapist.user.last_name,
            phone_number=therapist.user.phone_number,
        )
