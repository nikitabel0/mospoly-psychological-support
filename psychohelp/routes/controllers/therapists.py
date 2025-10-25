from uuid import UUID

from fastapi import HTTPException, APIRouter, Query

from psychohelp.config.logging import get_logger
from psychohelp.services.therapists import (
    get_therapist_by_id,
    get_therapists as srv_get_therapists,
)
from psychohelp.schemas.therapists import TherapistResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/therapists", tags=["therapists"])


@router.get("/{therapist_id}", response_model=TherapistResponse)
async def get_therapist(therapist_id: UUID) -> TherapistResponse:
    """
    Получить информацию о конкретном психологе по ID
    """
    therapist = await get_therapist_by_id(therapist_id)
    if therapist is None:
        logger.warning(f"Therapist not found: {therapist_id}")
        raise HTTPException(status_code=404, detail="Therapist not found")
    
    logger.info(f"Therapist retrieved: {therapist_id}")
    return TherapistResponse.from_orm_therapist(therapist)


@router.get("/", response_model=list[TherapistResponse])
async def get_therapists(
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    take: int = Query(10, gt=0, le=100, description="Количество записей для получения")
) -> list[TherapistResponse]:
    """
    Получить список всех психологов с пагинацией
    
    Args:
        skip: Количество записей для пропуска (offset)
        take: Количество записей для получения (limit)
    """
    logger.info(f"Fetching therapists: skip={skip}, take={take}")
    therapists = await srv_get_therapists(skip=skip, take=take)
    
    logger.info(f"Retrieved {len(therapists)} therapists")
    return [TherapistResponse.from_orm_therapist(t) for t in therapists]
