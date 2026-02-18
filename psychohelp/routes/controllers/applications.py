from uuid import UUID
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_200_OK

from psychohelp.config.logging import get_logger
from psychohelp.services.applications import (
    create_application,
    get_application_for_user,
    update_application_status,
)
from psychohelp.repositories.applications import get_applications as repo_get_applications
from psychohelp.schemas.applications import (
    ApplicationCreateRequest,
    ApplicationResponse,
    ApplicationUpdateRequest,
    ApplicationStatus,
)
from psychohelp.services.rbac.permissions import require_permission
from psychohelp.constants.rbac import PermissionCode
from psychohelp.repositories import get_user_id_from_token

logger = get_logger(__name__)
router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("/", response_model=ApplicationResponse, status_code=HTTP_201_CREATED)
async def create_application_endpoint(
    request: Request,
    data: ApplicationCreateRequest
) -> ApplicationResponse:
    token = request.cookies.get("access_token")
    user_id = get_user_id_from_token(token) if token else None

    application = await create_application(user_id, data)
    logger.info(f"Application created: {application.id}")
    return ApplicationResponse.from_orm(application)


@router.get("/", response_model=list[ApplicationResponse])
@require_permission(PermissionCode.APPOINTMENTS_VIEW_ALL)
async def get_applications(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: ApplicationStatus | None = None
) -> list[ApplicationResponse]:
    applications = await repo_get_applications(skip=skip, limit=limit, status=status)
    return [ApplicationResponse.from_orm(app) for app in applications]


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    request: Request,
    application_id: UUID
) -> ApplicationResponse:
    token = request.cookies.get("access_token")
    user_id = get_user_id_from_token(token) if token else None
    is_admin = False

    application = await get_application_for_user(application_id, user_id, is_admin)
    return ApplicationResponse.from_orm(application)


@router.patch("/{application_id}", response_model=ApplicationResponse)
@require_permission(PermissionCode.APPOINTMENTS_ACCEPT)
async def update_application(
    request: Request,
    application_id: UUID,
    data: ApplicationUpdateRequest
) -> ApplicationResponse:
    application = await update_application_status(application_id, data.status, is_admin=True)
    return ApplicationResponse.from_orm(application)