from uuid import UUID

from psychohelp.models.therapists import Therapist
from psychohelp.repositories.therapists import (
    get_therapist_by_id as repo_get_therapist_by_id,
    get_therapists as repo_get_therapists,
    create_therapist as repo_create_therapist,
    delete_therapist as repo_delete_therapist,
    UserNotFoundForTherapistException,
    PsychologistRoleNotFoundException,
    TherapistAlreadyExistsException,
)


async def get_therapist_by_id(therapist_id: UUID) -> Therapist | None:
    """
    Получить психолога по ID
    
    Args:
        therapist_id: UUID психолога
        
    Returns:
        Therapist | None: ORM модель психолога или None если не найден
    """
    return await repo_get_therapist_by_id(therapist_id)


async def get_therapists(skip: int = 0, take: int = 10) -> list[Therapist]:
    """
    Получить список всех психологов с пагинацией
    
    Args:
        skip: Количество записей для пропуска
        take: Количество записей для получения
        
    Returns:
        list[Therapist]: Список ORM моделей психологов
    """
    therapists = await repo_get_therapists(skip=skip, take=take)
    return list(therapists)


async def create_therapist(user_id: UUID, therapist_data: dict) -> Therapist:
    return await repo_create_therapist(user_id, therapist_data)


async def delete_therapist(therapist_id: UUID) -> bool:
    return await repo_delete_therapist(therapist_id)

