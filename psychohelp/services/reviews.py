from uuid import UUID

from psychohelp.repositories.reviews import (
    get_review,
    create_review as repo_create_review,
    get_reviews_by_psychologist as repo_get_reviews_by_psychologist
)
from psychohelp.repositories.appointments import get_appointment_by_id


async def get_review_by_id(appointment_id: UUID):
    return await get_review(appointment_id)


async def create_review(appointment_id: UUID, content: str):
    """Создать отзыв для записи на прием"""
    # Проверяем, существует ли запись на прием
    appointment = await get_appointment_by_id(appointment_id)
    if not appointment:
        raise ValueError("Запись на прием не найдена")
    
    # Проверяем, нет ли уже отзыва
    existing_review = await get_review(appointment_id)
    if existing_review:
        raise ValueError("Отзыв для этой записи уже существует")
    
    return await repo_create_review(appointment_id, content)


async def get_reviews_by_psychologist(psychologist_id: UUID, skip: int = 0, take: int = 10):
    """Получить отзывы для конкретного психолога"""
    return await repo_get_reviews_by_psychologist(psychologist_id, skip, take)
