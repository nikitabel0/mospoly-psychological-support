from uuid import UUID

from fastapi import HTTPException, APIRouter, Query, Request
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

from psychohelp.config.logging import get_logger
from psychohelp.services.psychologists import (
    get_psychologist_by_id,
    get_psychologists as srv_get_psychologists,
    create_psychologist,
    delete_psychologist,
)
from psychohelp.repositories.psychologists.exceptions import (
    UserNotFoundForPsychologistException,
    PsychologistRoleNotFoundException,
    PsychologistAlreadyExistsException,
)
from psychohelp.schemas.psychologists import PsychologistResponse, PsychologistCreateRequest
from psychohelp.services.rbac.permissions import require_permission
from psychohelp.constants.rbac import PermissionCode

logger = get_logger(__name__)
router = APIRouter(prefix="/therapists", tags=["therapists"])


@router.get("/{psychologist_id}", response_model=PsychologistResponse)
@require_permission(PermissionCode.PSYCHOLOGISTS_VIEW)
async def get_psychologist(request: Request, psychologist_id: UUID) -> PsychologistResponse:
    """Получить информацию о конкретном психологе по ID"""
    psychologist = await get_psychologist_by_id(psychologist_id)
    if psychologist is None:
        logger.warning(f"Psychologist not found: {psychologist_id}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Psychologist not found")
    
    logger.info(f"Psychologist retrieved: {psychologist_id}")
    return PsychologistResponse.from_orm_psychologist(psychologist)


@router.get("/", response_model=list[PsychologistResponse])
@require_permission(PermissionCode.PSYCHOLOGISTS_VIEW)
async def get_psychologists(
    request: Request,
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    take: int = Query(10, gt=0, le=100, description="Количество записей для получения")
) -> list[PsychologistResponse]:
    """Получить список всех психологов с пагинацией"""
    logger.info(f"Fetching psychologists: skip={skip}, take={take}")
    psychologists = await srv_get_psychologists(skip=skip, take=take)
    
    logger.info(f"Retrieved {len(psychologists)} psychologists")
    return [PsychologistResponse.from_orm_psychologist(p) for p in psychologists]


@router.post("/", response_model=PsychologistResponse, status_code=HTTP_201_CREATED)
@require_permission(PermissionCode.PSYCHOLOGISTS_MANAGE)
async def create_psychologist_endpoint(request: Request, data: PsychologistCreateRequest) -> PsychologistResponse:
    try:
        psychologist_data = data.model_dump(exclude={"user_id"})
        psychologist = await create_psychologist(data.user_id, psychologist_data)
        logger.info(f"Psychologist created: {psychologist.id} for user {data.user_id}")
        return PsychologistResponse.from_orm_psychologist(psychologist)
    
    except UserNotFoundForPsychologistException as e:
        logger.error(f"User not found: {data.user_id}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(e))
    
    except PsychologistRoleNotFoundException as e:
        logger.error("Psychologist role not found in database")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    except PsychologistAlreadyExistsException as e:
        logger.warning(f"Psychologist already exists for user: {data.user_id}")
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{psychologist_id}")
@require_permission(PermissionCode.PSYCHOLOGISTS_MANAGE)
async def delete_psychologist_endpoint(request: Request, psychologist_id: UUID) -> dict[str, str]:
    deleted = await delete_psychologist(psychologist_id)
    if not deleted:
        logger.warning(f"Psychologist not found for deletion: {psychologist_id}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Psychologist not found")
    
    logger.info(f"Psychologist deleted: {psychologist_id}")
    return {"message": "Psychologist successfully deleted"}

