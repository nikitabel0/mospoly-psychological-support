from datetime import datetime, timezone
from uuid import UUID

from psychohelp.repositories import get_user_id_from_token
from psychohelp.repositories.appointments import (
    get_appointment_by_id as repo_get_appointment_by_id,
    create_appointment as repo_create_appointment,
    cancel_appointment_by_id as repo_cancel_appointment_by_id,
    get_appointments_by_user_id as repo_get_appointments_by_user_id,
)
from psychohelp.repositories.psychologists.psychologists import get_psychologist_by_id
from psychohelp.repositories.users import get_user_by_id
from psychohelp.models.appointments import Appointment, AppointmentType, AppointmentStatus
from psychohelp.services.appointments import exceptions as exc


async def get_appointment_by_id(appointment_id: UUID) -> Appointment | None:
    return await repo_get_appointment_by_id(appointment_id)


async def create_appointment(
    patient_id: UUID,
    psychologist_id: UUID,
    type: AppointmentType,
    scheduled_time: datetime,
    reason: str | None = None,
    remind_time: datetime | None = None,
    venue: str | None = None,
    comment: str | None = None,
) -> Appointment:
    """
    Создание записи на прием к психологу
    
    Args:
        patient_id: ID пациента
        psychologist_id: ID психолога
        type: Тип консультации (онлайн/офлайн)
        scheduled_time: Время назначенной встречи
        reason: Причина обращения
        remind_time: Время напоминания
        venue: Место встречи (для онлайн)
        comment: Комментарий к записи
        
    Raises:
        PatientNotFoundException: Если пациент не найден
        PsychologistNotFoundException: Если психолог не найден
        VenueRequiredException: Если не указано место для онлайн встречи
        InvalidScheduledTimeException: Если время записи в прошлом
        InvalidRemindTimeException: Если время напоминания некорректно
    """
    now = datetime.now(timezone.utc)
    status = AppointmentStatus.Accepted

    scheduled_time_utc = scheduled_time.astimezone(timezone.utc) if scheduled_time.tzinfo else scheduled_time.replace(tzinfo=timezone.utc)
    if scheduled_time_utc <= now:
        raise exc.InvalidScheduledTimeException(scheduled_time)

    if remind_time is not None:
        remind_time_utc = remind_time.astimezone(timezone.utc) if remind_time.tzinfo else remind_time.replace(tzinfo=timezone.utc)
        
        if remind_time_utc <= now:
            raise exc.InvalidRemindTimeException(remind_time, "время напоминания не может быть в прошлом")
        
        if remind_time_utc >= scheduled_time_utc:
            raise exc.InvalidRemindTimeException(remind_time, "время напоминания должно быть раньше времени встречи")

    patient = await get_user_by_id(patient_id)
    if patient is None:
        raise exc.PatientNotFoundException(patient_id)

    psychologist = await get_psychologist_by_id(psychologist_id)
    if psychologist is None:
        raise exc.PsychologistNotFoundException(psychologist_id)


    match type:
        case AppointmentType.Offline:
            venue = psychologist.office
        
        case AppointmentType.Online:
            if venue is None:
                raise exc.VenueRequiredException()

    return await repo_create_appointment(
        patient_id,
        psychologist.id,
        type,
        reason,
        status,
        scheduled_time,
        remind_time,
        now,
        venue,
        comment,
    )


async def cancel_appointment_by_id(appointment_id: UUID) -> Appointment:
    return await repo_cancel_appointment_by_id(appointment_id)


async def get_appointments_by_user_id(user_id: UUID) -> list[Appointment]:
    return await repo_get_appointments_by_user_id(user_id)


async def get_appointments_by_token(token: str) -> list[Appointment]:
    id = get_user_id_from_token(token)
    return await get_appointments_by_user_id(id)

