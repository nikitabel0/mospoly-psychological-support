from uuid import UUID

from psychohelp.models.articles import Article
from psychohelp.repositories import articles as repo


async def get_articles(skip: int = 0, take: int = 100) -> list[Article]:
    return await repo.get_articles(skip=skip, take=take)


async def get_article_by_id(article_id: UUID) -> Article | None:
    return await repo.get_article_by_id(article_id)


async def create_article(article_data: dict) -> Article:
    return await repo.create_article(article_data)


async def update_article(article_id: UUID, article_data: dict) -> Article | None:
    return await repo.update_article(article_id, article_data)


async def delete_article(article_id: UUID) -> bool:
    return await repo.delete_article(article_id)
