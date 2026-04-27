from uuid import UUID

from psychohelp.models.news import News
from psychohelp.repositories import news as news_repo


async def get_news_list(skip: int = 0, take: int = 100) -> list[News]:
    return await news_repo.get_news_list(skip, take)


async def get_news_by_id(news_id: UUID) -> News | None:
    return await news_repo.get_news_by_id(news_id)


async def create_news(news_data: dict) -> News:
    return await news_repo.create_news(news_data)


async def update_news(news_id: UUID, news_data: dict) -> News | None:
    return await news_repo.update_news(news_id, news_data)


async def delete_news(news_id: UUID) -> bool:
    return await news_repo.delete_news(news_id)