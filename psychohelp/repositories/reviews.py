from psychohelp.models.reviews import Review
from psychohelp.config.database import get_async_db

from sqlalchemy import select
from datetime import datetime

from uuid import UUID


async def get_review(appointment_id: UUID):
    async with get_async_db() as session:
        result = await session.execute(
            select(Review).filter(Review.appointment_id == appointment_id)
        )
    return result.scalar_one_or_none()


async def create_review(appointment_id: UUID, content: str) -> Review:
    """Создать новый отзыв для записи на прием"""
    async with get_async_db() as session:
        review = Review(
            appointment_id=appointment_id,
            time=datetime.utcnow(),
            content=content
        )
        session.add(review)
        await session.commit()
        await session.refresh(review)
        return review


async def get_reviews_by_psychologist(psychologist_id: UUID, skip: int = 0, take: int = 10):
    """Получить отзывы для конкретного психолога"""
    from psychohelp.models.appointments import Appointment
    
    async with get_async_db() as session:
        result = await session.execute(
            select(Review)
            .join(Appointment, Review.appointment_id == Appointment.id)
            .filter(Appointment.psychologist_id == psychologist_id)
            .offset(skip)
            .limit(take)
            .order_by(Review.time.desc())
        )
        return result.scalars().all()
