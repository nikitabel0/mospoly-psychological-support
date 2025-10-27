from uuid import UUID

from fastapi import HTTPException, APIRouter, Query, Request
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

from psychohelp.config.logging import get_logger
from psychohelp.services.therapists import (
    get_therapist_by_id,
    get_therapists as srv_get_therapists,
    create_therapist,
    delete_therapist,
    UserNotFoundForTherapistException,
    PsychologistRoleNotFoundException,
    TherapistAlreadyExistsException,
)
from psychohelp.schemas.therapists import TherapistResponse, TherapistCreateRequest
from psychohelp.services.rbac import require_permission
from psychohelp.constants import PermissionCode

logger = get_logger(__name__)
router = APIRouter(prefix="/therapists", tags=["therapists"])


@router.get("/{therapist_id}", response_model=TherapistResponse)
async def get_therapist(therapist_id: UUID) -> TherapistResponse:
    """Получить информацию о конкретном психологе по ID"""
    therapist = await get_therapist_by_id(therapist_id)
    if therapist is None:
        logger.warning(f"Therapist not found: {therapist_id}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Therapist not found")
    
    logger.info(f"Therapist retrieved: {therapist_id}")
    return TherapistResponse.from_orm_therapist(therapist)


@router.get("/", response_model=list[TherapistResponse])
async def get_therapists(
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    take: int = Query(10, gt=0, le=100, description="Количество записей для получения")
) -> list[TherapistResponse]:
    """Получить список всех психологов с пагинацией"""
    logger.info(f"Fetching therapists: skip={skip}, take={take}")
    therapists = await srv_get_therapists(skip=skip, take=take)
    
    logger.info(f"Retrieved {len(therapists)} therapists")
    return [TherapistResponse.from_orm_therapist(t) for t in therapists]


@router.post("/", response_model=TherapistResponse, status_code=HTTP_201_CREATED)
@require_permission(PermissionCode.THERAPISTS_MANAGE.value)
async def create_therapist_endpoint(request: Request, data: TherapistCreateRequest) -> TherapistResponse:
    try:
        therapist_data = data.model_dump(exclude={"user_id"})
        therapist = await create_therapist(data.user_id, therapist_data)
        logger.info(f"Therapist created: {therapist.id} for user {data.user_id}")
        return TherapistResponse.from_orm_therapist(therapist)
    
    except UserNotFoundForTherapistException as e:
        logger.error(f"User not found: {data.user_id}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(e))
    
    except PsychologistRoleNotFoundException as e:
        logger.error("Psychologist role not found in database")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    except TherapistAlreadyExistsException as e:
        logger.warning(f"Therapist already exists for user: {data.user_id}")
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{therapist_id}")
@require_permission(PermissionCode.THERAPISTS_MANAGE.value)
async def delete_therapist_endpoint(request: Request, therapist_id: UUID):
    deleted = await delete_therapist(therapist_id)
    if not deleted:
        logger.warning(f"Therapist not found for deletion: {therapist_id}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Therapist not found")
    
    logger.info(f"Therapist deleted: {therapist_id}")
    return {"message": "Therapist successfully deleted"}

