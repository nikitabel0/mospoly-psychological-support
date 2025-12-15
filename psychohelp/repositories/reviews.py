from psychohelp.models.reviews import Review
from psychohelp.config.config import get_async_db

from sqlalchemy import select

from uuid import UUID


async def get_review(appointment_id: UUID):
    async with get_async_db() as session:
        result = await session.execute(
            select(Review).filter(Review.appointment_id == appointment_id)
        )
    return result.scalar_one_or_none()
