from uuid import UUID

from sqlalchemy import select, update

from psychohelp.config.config import get_async_db
from psychohelp.models.articles import Article


async def get_articles(skip: int = 0, take: int = 100) -> list[Article]:
    async with get_async_db() as session:
        result = await session.execute(
            select(Article)
            .order_by(Article.title.asc())
            .offset(skip)
            .limit(take)
        )
        return list(result.scalars().all())


async def get_article_by_id(article_id: UUID) -> Article | None:
    async with get_async_db() as session:
        result = await session.execute(
            select(Article).where(Article.id == article_id)
        )
        return result.scalar_one_or_none()


async def create_article(article_data: dict) -> Article:
    async with get_async_db() as session:
        article = Article(**article_data)
        session.add(article)
        await session.commit()
        await session.refresh(article)
        return article


async def update_article(article_id: UUID, article_data: dict) -> Article | None:
    async with get_async_db() as session:
        stmt = (
            update(Article)
            .where(Article.id == article_id)
            .values(**article_data)
            .returning(Article)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.scalar_one_or_none()


async def delete_article(article_id: UUID) -> bool:
    async with get_async_db() as session:
        article = await session.get(Article, article_id)
        if article is None:
            return False

        await session.delete(article)
        await session.commit()
        return True
