from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.status import HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from psychohelp.config.logging import get_logger
from psychohelp.constants.rbac import RoleCode
from psychohelp.dependencies.auth import get_current_user
from psychohelp.models.users import User
from psychohelp.schemas.articles import (
    ArticleCreateRequest,
    ArticleResponse,
    ArticleUpdateRequest,
)
from psychohelp.services import articles as articles_service


logger = get_logger(__name__)
router = APIRouter(prefix="/articles", tags=["articles"])


def _ensure_admin(user: User) -> None:
    role_codes = {
        getattr(getattr(role, "code", role), "value", getattr(role, "code", role))
        for role in (user.roles or [])
    }
    if RoleCode.ADMIN.value not in role_codes:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Доступ запрещен. Только для администраторов.",
        )


@router.get("/", response_model=list[ArticleResponse])
async def get_articles(
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    take: int = Query(100, gt=0, le=100, description="Количество записей для получения"),
) -> list[ArticleResponse]:
    articles = await articles_service.get_articles(skip=skip, take=take)
    return articles


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: UUID) -> ArticleResponse:
    article = await articles_service.get_article_by_id(article_id)
    if article is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Статья не найдена")
    return article


@router.post("/", response_model=ArticleResponse, status_code=HTTP_201_CREATED)
async def create_article(
    data: ArticleCreateRequest,
    current_user: User = Depends(get_current_user),
) -> ArticleResponse:
    _ensure_admin(current_user)
    article = await articles_service.create_article(data.model_dump())
    logger.info(f"Article created: {article.id}")
    return article


@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: UUID,
    data: ArticleUpdateRequest,
    current_user: User = Depends(get_current_user),
) -> ArticleResponse:
    _ensure_admin(current_user)
    article = await articles_service.update_article(article_id, data.model_dump())
    if article is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Статья не найдена")
    logger.info(f"Article updated: {article_id}")
    return article


@router.delete("/{article_id}")
async def delete_article(
    article_id: UUID,
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    _ensure_admin(current_user)
    deleted = await articles_service.delete_article(article_id)
    if not deleted:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Статья не найдена")
    logger.info(f"Article deleted: {article_id}")
    return {"message": "Статья успешно удалена"}
