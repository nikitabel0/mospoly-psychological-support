
from uuid import UUID
from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN

from psychohelp.repositories import applications as repo
from psychohelp.models.applications import Application, ApplicationStatus
from psychohelp.repositories.users import get_user_by_id
from psychohelp.schemas.applications import ApplicationCreateRequest


async def create_application(
    user_id: UUID | None,
    data: ApplicationCreateRequest
) -> Application:
    application_dict = data.model_dump()
    if user_id:
        user = await get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
        application_dict["user_id"] = user_id
    else:
        application_dict["user_id"] = None

    return await repo.create_application(application_dict)


async def get_application_for_user(application_id: UUID, user_id: UUID | None, is_admin: bool) -> Application:
    application = await repo.get_application_by_id(application_id)
    if not application:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Application not found")

    if not is_admin and application.user_id != user_id:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access denied")

    return application


async def update_application_status(application_id: UUID, status: ApplicationStatus, is_admin: bool) -> Application:
    if not is_admin:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Only admins can update status")

    application = await repo.get_application_by_id(application_id)
    if not application:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Application not found")

    updated = await repo.update_application(application_id, {"status": status})
    return updated