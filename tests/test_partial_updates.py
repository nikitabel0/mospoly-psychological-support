from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import httpx
import pytest
from pydantic import ValidationError

from psychohelp.constants.rbac import RoleCode
from psychohelp.dependencies.auth import get_current_user
from psychohelp.main import app
from psychohelp.routes.controllers import articles as articles_controller
from psychohelp.routes.controllers import news as news_controller
from psychohelp.schemas.articles import ArticleUpdateRequest
from psychohelp.schemas.news import NewsUpdateRequest
from psychohelp.schemas.users import UserUpdateRequest
from psychohelp.services.rbac import permissions as permissions_service


@pytest.mark.parametrize(
    "schema,field",
    [
        (ArticleUpdateRequest, "slug"),
        (ArticleUpdateRequest, "title"),
        (ArticleUpdateRequest, "text"),
        (NewsUpdateRequest, "slug"),
        (NewsUpdateRequest, "title"),
        (NewsUpdateRequest, "event_date"),
        (UserUpdateRequest, "first_name"),
        (UserUpdateRequest, "last_name"),
        (UserUpdateRequest, "phone_number"),
        (UserUpdateRequest, "email"),
    ],
)
def test_required_fields_cannot_be_null(schema, field):
    with pytest.raises(ValidationError):
        schema.model_validate({field: None})


@pytest.mark.parametrize(
    "schema,field",
    [
        (ArticleUpdateRequest, "image"),
        (ArticleUpdateRequest, "date"),
        (ArticleUpdateRequest, "author"),
        (ArticleUpdateRequest, "description"),
        (NewsUpdateRequest, "image"),
        (NewsUpdateRequest, "type"),
        (NewsUpdateRequest, "description"),
        (NewsUpdateRequest, "link"),
        (NewsUpdateRequest, "text"),
        (UserUpdateRequest, "middle_name"),
        (UserUpdateRequest, "social_media"),
        (UserUpdateRequest, "study_group"),
    ],
)
def test_optional_fields_can_be_cleared_with_null(schema, field):
    data = schema.model_validate({field: None})

    assert data.model_dump(exclude_unset=True) == {field: None}


async def _put(path, payload):
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.put(path, json=payload)


@pytest.fixture
def admin(monkeypatch):
    async def fake_current_user():
        return SimpleNamespace(
            id=uuid4(),
            roles=[SimpleNamespace(code=RoleCode.ADMIN)],
        )

    async def fake_has_permission(_user_id, _permission_code):
        return True

    app.dependency_overrides[get_current_user] = fake_current_user
    monkeypatch.setattr(permissions_service, "user_has_permission", fake_has_permission)
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_article_update_passes_only_sent_fields(monkeypatch, admin):
    article_id = uuid4()
    received = {}

    async def fake_update_article(_article_id, article_data):
        received.update(article_data)
        return SimpleNamespace(
            id=article_id,
            slug="slug",
            image=None,
            date=None,
            author=None,
            title="Новый заголовок",
            description=None,
            text="Текст",
        )

    monkeypatch.setattr(
        articles_controller.articles_service, "update_article", fake_update_article
    )

    response = await _put(
        f"/articles/{article_id}", {"title": "Новый заголовок", "image": None}
    )

    assert response.status_code == 200, response.text
    assert received == {"title": "Новый заголовок", "image": None}


@pytest.mark.asyncio
async def test_article_update_rejects_null_for_required_field(admin):
    response = await _put(f"/articles/{uuid4()}", {"text": None})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_news_update_passes_only_sent_fields(monkeypatch, admin):
    news_id = uuid4()
    received = {}
    now = datetime.now(timezone.utc)

    async def fake_update_news(_news_id, news_data):
        received.update(news_data)
        return SimpleNamespace(
            id=news_id,
            slug="slug",
            image=None,
            type=None,
            date=now,
            event_date=now,
            title="Новый заголовок",
            description=None,
            link=None,
            text=None,
        )

    monkeypatch.setattr(news_controller.news_service, "update_news", fake_update_news)

    response = await _put(
        f"/news/{news_id}", {"title": "Новый заголовок", "link": None}
    )

    assert response.status_code == 200, response.text
    assert received == {"title": "Новый заголовок", "link": None}


@pytest.mark.asyncio
async def test_news_update_rejects_null_for_required_field(admin):
    response = await _put(f"/news/{uuid4()}", {"event_date": None})

    assert response.status_code == 422
