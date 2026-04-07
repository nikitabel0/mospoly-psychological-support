from uuid import UUID

from psychohelp.models.psychologists import Psychologist
from psychohelp.repositories.psychologists.psychologists import (
    get_psychologist_by_id as repo_get_psychologist_by_id,
    get_psychologists as repo_get_psychologists,
    create_psychologist as repo_create_psychologist,
    update_psychologist as repo_update_psychologist,
    delete_psychologist as repo_delete_psychologist,
)


async def get_psychologist_by_id(psychologist_id: UUID) -> Psychologist | None:
    """Получить психолога по ID."""
    return await repo_get_psychologist_by_id(psychologist_id)


async def get_psychologists(skip: int = 0, take: int = 10) -> list[Psychologist]:
    """Получить список всех психологов с пагинацией."""
    psychologists = await repo_get_psychologists(skip=skip, take=take)
    return list(psychologists)


async def create_psychologist(user_id: UUID, psychologist_data: dict) -> Psychologist:
    return await repo_create_psychologist(user_id, psychologist_data)


async def update_psychologist(psychologist_id: UUID, psychologist_data: dict) -> Psychologist | None:
    return await repo_update_psychologist(psychologist_id, psychologist_data)


async def delete_psychologist(psychologist_id: UUID) -> bool:
    return await repo_delete_psychologist(psychologist_id)
