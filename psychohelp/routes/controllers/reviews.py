from fastapi import HTTPException, APIRouter, Request, Query
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from psychohelp.services.reviews import (
    get_review_by_id,
    create_review as srv_create_review,
    get_reviews_by_psychologist,
    UUID
)
from psychohelp.schemas.reviews import ReviewsBase, ReviewCreateRequest
from psychohelp.services.rbac.permissions import require_permission
from psychohelp.constants.rbac import PermissionCode
from psychohelp.config.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/{review_id}", response_model=ReviewsBase)
@require_permission(PermissionCode.REVIEWS_VIEW_ALL)
async def get_review(request: Request, review_id: UUID):
    """Получить отзыв по ID записи на прием"""
    review = await get_review_by_id(review_id)
    if review is None:
        logger.warning(f"Review not found: {review_id}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Review not found")
    logger.info(f"Review retrieved: {review_id}")
    return review


@router.post("/", response_model=ReviewsBase, status_code=HTTP_201_CREATED)
@require_permission(PermissionCode.REVIEWS_CREATE_OWN)
async def create_review(request: Request, data: ReviewCreateRequest) -> ReviewsBase:
    """Создать новый отзыв"""
    try:
        review = await srv_create_review(data.appointment_id, data.content)
        logger.info(f"Review created for appointment: {data.appointment_id}")
        return review
    except ValueError as e:
        logger.error(f"Failed to create review: {str(e)}")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/psychologist/{psychologist_id}", response_model=list[ReviewsBase])
@require_permission(PermissionCode.REVIEWS_VIEW_ALL)
async def get_psychologist_reviews(
    request: Request,
    psychologist_id: UUID,
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    take: int = Query(10, gt=0, le=100, description="Количество записей для получения")
) -> list[ReviewsBase]:
    """Получить отзывы для конкретного психолога"""
    logger.info(f"Fetching reviews for psychologist: {psychologist_id}")
    reviews = await get_reviews_by_psychologist(psychologist_id, skip, take)
    logger.info(f"Retrieved {len(reviews)} reviews")
    return reviews
