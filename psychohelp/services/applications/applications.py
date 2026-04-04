from uuid import UUID
from typing import Optional
from datetime import datetime, timezone
from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN, HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY

from psychohelp.repositories import applications as repo
from psychohelp.services.applications.state_machine import ApplicationStateMachine
from psychohelp.services.applications.exceptions import (
    ApplicationNotFoundError, InvalidStatusTransitionError, AccessDeniedError,
    ConflictError, ValidationError
)
from psychohelp.schemas.applications import ApplicationCreateRequest, OfferConsultationRequest
from psychohelp.models.applications import Application, ApplicationStatus
from psychohelp.repositories.users import get_user_by_id


async def create_application(user_id: UUID | None, data: ApplicationCreateRequest) -> Application:
    application_dict = data.model_dump()
    if user_id:
        user = await get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
        application_dict["user_id"] = user_id
    else:
        application_dict["user_id"] = None
    # Для неавторизованных проверяем наличие контакта
    if not application_dict.get("email") and not application_dict.get("phone"):
        raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail="Необходимо указать email или телефон")
    return await repo.create_application(application_dict)


async def get_application_for_user(application_id: UUID, user_id: UUID | None, is_manager_or_psychologist: bool) -> Application:
    application = await repo.get_application_by_id(application_id)
    if not application:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Application not found")
    if not is_manager_or_psychologist and application.user_id != user_id:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access denied")
    return application


async def accept_to_processing(
    application_id: UUID,
    assigned_to: UUID,
    actor_id: UUID,
    is_allowed: bool
) -> Application:
    if not is_allowed:
        raise AccessDeniedError()
    application = await repo.get_application_by_id(application_id)
    if not application:
        raise ApplicationNotFoundError()
    sm = ApplicationStateMachine(application)
    try:
        updated = await sm.accept_to_processing(assigned_to, actor_id, "psychologist" if is_allowed else "manager")
        return updated
    except (InvalidStatusTransitionError, ConflictError, ValidationError) as e:
        raise e


async def offer_consultation(
    application_id: UUID,
    offer_data: OfferConsultationRequest,
    actor_id: UUID,
    is_psychologist: bool
) -> Application:
    if not is_psychologist:
        raise AccessDeniedError()
    application = await repo.get_application_by_id(application_id)
    if not application:
        raise ApplicationNotFoundError()
    sm = ApplicationStateMachine(application)
    try:
        updated = await sm.offer_consultation(offer_data.model_dump(), actor_id, "psychologist")
        return updated
    except (InvalidStatusTransitionError, ConflictError, ValidationError) as e:
        raise e


async def confirm_application(
    application_id: UUID,
    appointment_id: UUID,
    actor_id: UUID,
    is_owner: bool
) -> Application:
    if not is_owner:
        raise AccessDeniedError()
    application = await repo.get_application_by_id(application_id)
    if not application:
        raise ApplicationNotFoundError()
    sm = ApplicationStateMachine(application)
    try:
        updated = await sm.confirm(actor_id, "user", appointment_id)
        return updated
    except (InvalidStatusTransitionError, ConflictError, ValidationError) as e:
        raise e


async def reject_application(
    application_id: UUID,
    reject_reason: str,
    actor_id: UUID,
    is_allowed: bool
) -> Application:
    if not is_allowed:
        raise AccessDeniedError()
    application = await repo.get_application_by_id(application_id)
    if not application:
        raise ApplicationNotFoundError()
    sm = ApplicationStateMachine(application)
    try:
        updated = await sm.reject(reject_reason, actor_id, "psychologist" if is_allowed else "manager")
        return updated
    except (InvalidStatusTransitionError, ConflictError, ValidationError) as e:
        raise e


async def cancel_application(
    application_id: UUID,
    cancel_reason: str,
    cancel_initiator: str,
    actor_id: UUID,
    actor_type: str,
    is_allowed: bool
) -> Application:
    if not is_allowed:
        raise AccessDeniedError()
    application = await repo.get_application_by_id(application_id)
    if not application:
        raise ApplicationNotFoundError()
    sm = ApplicationStateMachine(application)
    try:
        updated = await sm.cancel(cancel_reason, cancel_initiator, actor_id, actor_type)
        return updated
    except (InvalidStatusTransitionError, ConflictError, ValidationError) as e:
        raise e


async def expire_application(application_id: UUID) -> Application:
    application = await repo.get_application_by_id(application_id)
    if not application:
        raise ApplicationNotFoundError()
    sm = ApplicationStateMachine(application)
    try:
        updated = await sm.expire(None, "system")
        return updated
    except (InvalidStatusTransitionError, ConflictError) as e:
        raise e