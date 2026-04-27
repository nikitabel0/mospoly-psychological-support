from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from psychohelp.constants.rbac import RoleCode
from psychohelp.routes.controllers import articles as articles_controller
from psychohelp.schemas.articles import ArticleCreateRequest


@pytest.mark.asyncio
async def test_get_articles_is_public(monkeypatch):
    article_id = uuid4()

    async def fake_get_articles(skip, take):
        assert skip == 0
        assert take == 100
        return [
            SimpleNamespace(
                id=article_id,
                title="Заголовок",
                text="Текст статьи",
            )
        ]

    monkeypatch.setattr(articles_controller.articles_service, "get_articles", fake_get_articles)

    result = await articles_controller.get_articles(skip=0, take=100)

    assert len(result) == 1
    assert result[0].id == article_id
    assert result[0].title == "Заголовок"
    assert result[0].text == "Текст статьи"


@pytest.mark.asyncio
async def test_create_article_allows_admin(monkeypatch):
    article_id = uuid4()

    async def fake_create_article(article_data):
        assert article_data == {"title": "Заголовок", "text": "Текст статьи"}
        return SimpleNamespace(id=article_id, **article_data)

    monkeypatch.setattr(articles_controller.articles_service, "create_article", fake_create_article)

    current_user = SimpleNamespace(
        roles=[SimpleNamespace(code=RoleCode.ADMIN)]
    )

    result = await articles_controller.create_article(
        ArticleCreateRequest(title="Заголовок", text="Текст статьи"),
        current_user=current_user,
    )

    assert result.id == article_id
    assert result.title == "Заголовок"
    assert result.text == "Текст статьи"


@pytest.mark.asyncio
async def test_create_article_forbids_non_admin(monkeypatch):
    async def fake_create_article(_):
        raise AssertionError("service should not be called")

    monkeypatch.setattr(articles_controller.articles_service, "create_article", fake_create_article)

    current_user = SimpleNamespace(
        roles=[SimpleNamespace(code=RoleCode.USER)]
    )

    with pytest.raises(HTTPException) as exc:
        await articles_controller.create_article(
            ArticleCreateRequest(title="Заголовок", text="Текст статьи"),
            current_user=current_user,
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == "Доступ запрещен. Только для администраторов."
