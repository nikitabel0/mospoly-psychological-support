from uuid import UUID

from sqlalchemy import select, update

from psychohelp.config.config import get_async_db
from psychohelp.models.news import News


async def get_news_list(skip: int = 0, take: int = 100) -> list[News]:
    async with get_async_db() as session:
        result = await session.execute(
            select(News)
            .order_by(News.created_at.desc())
            .offset(skip)
            .limit(take)
        )
        return list(result.scalars().all())


async def get_news_by_id(news_id: UUID) -> News | None:
    async with get_async_db() as session:
        result = await session.execute(
            select(News).where(News.id == news_id)
        )
        return result.scalar_one_or_none()


async def create_news(news_data: dict) -> News:
    async with get_async_db() as session:
        news_item = News(**news_data)
        session.add(news_item)
        await session.commit()
        await session.refresh(news_item)
        return news_item


async def update_news(news_id: UUID, news_data: dict) -> News | None:
    async with get_async_db() as session:
        stmt = (
            update(News)
            .where(News.id == news_id)
            .values(**news_data)
            .returning(News)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.scalar_one_or_none()


async def delete_news(news_id: UUID) -> bool:
    async with get_async_db() as session:
        news_item = await session.get(News, news_id)
        if news_item is None:
            return False

        await session.delete(news_item)
        await session.commit()
        return True