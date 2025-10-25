from uuid import UUID

from psychohelp.models.therapists import Therapist
from psychohelp.repositories.therapists import (
    get_therapist_by_id as repo_get_therapist_by_id,
    get_therapists as repo_get_therapists,
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
