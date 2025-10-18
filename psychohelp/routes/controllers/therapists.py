from fastapi import HTTPException, APIRouter, Query, Request

from psychohelp.config.logging import get_logger
from psychohelp.services.therapists import get_therapist_by_id, get_therapists as srv_get_therapists, UUID
from psychohelp.schemas.therapists import TherapistBase

logger = get_logger(__name__)
router = APIRouter(prefix="/therapists", tags=["therapists"])


@router.get("/{therapist_id}", response_model=TherapistBase)
async def get_therapist(therapist_id: UUID) -> TherapistBase:
    therapist = await get_therapist_by_id(therapist_id)
    if therapist is None:
        logger.warning(f"Therapist not found: {therapist_id}")
        raise HTTPException(status_code=404, detail="Therapist not found")
    logger.info(f"Therapist retrieved: {therapist_id}")
    return therapist


@router.get("/", response_model=list[TherapistBase])
async def get_therapists(
    request: Request, skip: int = Query(0, ge=0), take: int = Query(10, gt=0)
) -> list[TherapistBase]:
    logger.info(f"Fetching therapists: skip={skip}, take={take}")
    therapists = await srv_get_therapists(skip=skip, take=take)
    if not therapists:
        logger.warning("No therapists found")
        raise HTTPException(status_code=404, detail="No therapists found")
    logger.info(f"Retrieved {len(therapists)} therapists")
    return therapists
