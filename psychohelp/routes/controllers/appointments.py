from fastapi import HTTPException, APIRouter, Response, Request

from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from psychohelp.config.logging import get_logger
from psychohelp.services.appointments import (
    get_appointment_by_id,
    create_appointment as srv_create_appointment,
    cancel_appointment_by_id,
    get_appointments_by_token,
    get_appointments_by_user_id,
    UUID,
)
from psychohelp.services.appointments import exceptions as exc
from psychohelp.schemas.appointments import AppointmentBase, AppointmentCreateRequest
from psychohelp.services.rbac import require_permission
from psychohelp.constants import PermissionCode

logger = get_logger(__name__)
router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("/", response_model=list[AppointmentBase])
async def get_appointments(request: Request, user_id: UUID | None = None) -> list[AppointmentBase]:
    """Получить список записей на прием"""
    if user_id is None:
        if "access_token" not in request.cookies:
            logger.warning("Unauthorized appointments access attempt")
            raise HTTPException(
                HTTP_401_UNAUTHORIZED, detail="Пользователь не авторизован"
            )
        token = request.cookies["access_token"]
        logger.info("Fetching appointments by token")
        return await get_appointments_by_token(token)

    logger.info(f"Fetching appointments for user: {user_id}")
    return await get_appointments_by_user_id(user_id)


@router.post("/create", response_model=AppointmentBase)
@require_permission(PermissionCode.APPOINTMENTS_CREATE_OWN.value)
async def create_appointment(request: Request, appointment: AppointmentCreateRequest) -> AppointmentBase:
    """Создать новую запись на прием к психологу"""
    try:
        created_appointment = await srv_create_appointment(**appointment.model_dump())
        logger.info(f"Appointment created: {created_appointment.id}")
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
            detail=f"Пациент не найден"
        )
    
    except exc.TherapistNotFoundException as e:
        logger.error(f"Therapist not found: {e.therapist_id}")
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Психолог не найден"
        )
    
    except exc.TherapistRoleNotFoundException as e:
        logger.error(f"User does not have therapist role: {e.user_id}")
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
@require_permission(PermissionCode.APPOINTMENTS_VIEW_OWN.value)
async def get_appointment(request: Request, id: UUID) -> AppointmentBase:
    """Получить информацию о конкретной записи"""
    appointment = await get_appointment_by_id(id)
    if appointment is None:
        logger.warning(f"Appointment not found: {id}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Встреча не найдена")
    logger.info(f"Appointment retrieved: {id}")
    return appointment


@router.put("/{id}/cancel")
@require_permission(PermissionCode.APPOINTMENTS_CANCEL_OWN.value)
async def cancel_appointment(request: Request, id: UUID) -> Response:
    """Отменить запись на прием"""
    try:
        await cancel_appointment_by_id(id)
        logger.info(f"Appointment cancelled: {id}")
        return Response(None, status_code=HTTP_200_OK)
    except ValueError as e:
        logger.error(f"Appointment cancellation failed: {str(e)}")
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
