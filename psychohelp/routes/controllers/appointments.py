from fastapi import APIRouter, HTTPException, Request, Response
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
)

from psychohelp.config.logging import get_logger
from psychohelp.schemas.appointments import AppointmentBase, AppointmentCreateRequest
from psychohelp.services.appointments import (
    UUID,
    cancel_appointment_by_id,
    get_appointment_by_id,
    get_appointments_by_token,
    get_appointments_by_user_id,
)
from psychohelp.services.appointments import (
    create_appointment as srv_create_appointment,
)

logger = get_logger(__name__)
router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("/", response_model=list[AppointmentBase])
async def get_appointments(
    request: Request, user_id: UUID | None = None
) -> list[AppointmentBase]:
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
async def create_appointment(
    appointment: AppointmentCreateRequest, request: Request
) -> AppointmentBase:
    try:
        created_appointment = await srv_create_appointment(**appointment.model_dump())
        logger.info(f"Appointment created: {created_appointment.id}")
        return created_appointment
    except ValueError as e:
        logger.error(f"Appointment creation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{id}", response_model=AppointmentBase)
async def get_appointment(id: UUID) -> AppointmentBase:
    appointment = await get_appointment_by_id(id)
    if appointment is None:
        logger.warning(f"Appointment not found: {id}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Встреча не найдена")
    logger.info(f"Appointment retrieved: {id}")
    return appointment


@router.put("/{id}/cancel")
async def cancel_appointment(id: UUID) -> Response:
    try:
        await cancel_appointment_by_id(id)
        logger.info(f"Appointment cancelled: {id}")
        return Response(None, status_code=HTTP_200_OK)
    except ValueError as e:
        logger.error(f"Appointment cancellation failed: {str(e)}")
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
