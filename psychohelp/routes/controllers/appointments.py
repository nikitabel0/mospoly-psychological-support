from fastapi import HTTPException, APIRouter, Response, Request, Depends
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from uuid import UUID
from psychohelp.config.logging import get_logger
from psychohelp.services.appointments.appointments import (
    get_appointment_for_user,
    create_appointment as srv_create_appointment,
    cancel_appointment_by_patient,
    get_appointments_by_user_id,
)
from psychohelp.services.appointments import exceptions as exc
from psychohelp.schemas.appointments import AppointmentBase, AppointmentCreateRequest
from psychohelp.services.rbac.permissions import require_permission, user_has_permission
from psychohelp.constants.rbac import PermissionCode

from psychohelp.repositories import get_user_id_from_token
from psychohelp.dependencies import get_current_user, get_optional_user
from psychohelp.models.users import User

logger = get_logger(__name__)
router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("/", response_model=list[AppointmentBase])
async def get_appointments(
    user_id: UUID | None = None,
    current_user: User = Depends(get_optional_user)
) -> list[AppointmentBase]:
    """Получить список записей на прием"""
    if user_id is None:
        if current_user is None:
            logger.warning("Unauthorized appointments access attempt")
            raise HTTPException(
                HTTP_401_UNAUTHORIZED, detail="Пользователь не авторизован"
            )
        logger.info(f"Fetching appointments for current user: {current_user.id}")
        return await get_appointments_by_user_id(current_user.id)

    if current_user is None:
        logger.warning(f"Unauthorized access attempt to user {user_id} appointments")
        raise HTTPException(
            HTTP_401_UNAUTHORIZED, detail="Пользователь не авторизован"
        )
    
    if current_user.id != user_id and not getattr(current_user, 'is_admin', False):
        logger.warning(f"Access denied to user {user_id} appointments by user {current_user.id}")
        raise HTTPException(
            HTTP_401_UNAUTHORIZED, detail="Недостаточно прав для просмотра записей другого пользователя"
        )

    logger.info(f"Fetching appointments for user: {user_id}")
    return await get_appointments_by_user_id(user_id)


@router.post("/create", response_model=AppointmentBase)
@require_permission(PermissionCode.APPOINTMENTS_CREATE_OWN)
async def create_appointment(
    request: Request,
    appointment: AppointmentCreateRequest,
    current_user: User = Depends(get_current_user)
) -> AppointmentBase:
    """Создать новую запись на прием к психологу"""
    try:
        if appointment.patient_id != current_user.id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Вы можете создавать записи только для себя"
            )

        created_appointment = await srv_create_appointment(**appointment.model_dump())
        logger.info(f"Appointment created: {created_appointment.id} by user: {current_user.id}")
        return created_appointment
    
    except exc.InvalidScheduledTimeException as e:
        logger.error(f"Invalid scheduled time: {e.scheduled_time}")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Время записи не может быть в прошлом"
        )
    
    except exc.InvalidRemindTimeException as e:
        logger.error(f"Invalid remind time: {e.remind_time}, reason: {e.reason}")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Некорректное время напоминания: {e.reason}"
        )
    
    except exc.PatientNotFoundException as e:
        logger.error(f"Patient not found: {e.patient_id}")
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Пациент не найден"
        )

    except exc.PsychologistNotFoundException as e:
        logger.error(f"Psychologist not found: {e.psychologist_id}")
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Психолог не найден"
        )
    
    except exc.PsychologistRoleNotFoundException as e:
        logger.error(f"User does not have psychologist role: {e.user_id}")
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Указанный пользователь не является психологом"
        )
    
    except exc.VenueRequiredException:
        logger.error("Venue required for online appointment")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Необходимо указать место для онлайн встречи"
        )
    
    except Exception as e:
        logger.exception(f"Unexpected error during appointment creation: {str(e)}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось создать запись на прием"
        )


@router.get("/{id}", response_model=AppointmentBase)
@require_permission(PermissionCode.APPOINTMENTS_VIEW_OWN)
async def get_appointment(
    request: Request,
    id: UUID,
    current_user: User = Depends(get_current_user)
) -> AppointmentBase:
    """Получить информацию о конкретной записи"""
    appointment = await get_appointment_for_user(id, current_user.id)
    if appointment is None:
        logger.warning(f"Appointment not found or access denied: {id} for user: {current_user.id}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Встреча не найдена")
    
    logger.info(f"Appointment retrieved: {id} by user: {current_user.id}")
    return appointment


@router.put("/{id}/cancel")
@require_permission(PermissionCode.APPOINTMENTS_CANCEL_OWN)
async def cancel_appointment(
    request: Request,
    id: UUID,
    current_user: User = Depends(get_current_user)
) -> Response:
    """Отменить запись на прием (для пациента)"""
    try:
        await cancel_appointment_by_patient(id, current_user.id)
        logger.info(f"Appointment cancelled: {id} by user: {current_user.id}")
        return Response(None, status_code=HTTP_200_OK)
    except ValueError as e:
        logger.error(f"Appointment cancellation failed: {str(e)}")
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
