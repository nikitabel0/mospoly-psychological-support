from datetime import datetime, timezone

from psychohelp.repositories import get_user_id_from_token
from psychohelp.repositories.appointments import (
    get_appointment_by_id as repo_get_appointment_by_id,
    create_appointment as repo_create_appointment,
    cancel_appointment_by_id as repo_cancel_appointment_by_id,
    get_appointments_by_user_id as repo_get_appointments_by_user_id,
    UUID,
)
from psychohelp.repositories.therapists import get_therapist_by_id
from psychohelp.repositories.users import get_user_by_id
from psychohelp.models.appointments import AppointmentType, AppointmentStatus
from psychohelp.services.appointments import exceptions as exc


async def get_appointment_by_id(appointment_id: UUID):
    return await repo_get_appointment_by_id(appointment_id)


async def create_appointment(
    patient_id: UUID,
    therapist_id: UUID,
    type: AppointmentType,
    scheduled_time: datetime,
    reason: str | None = None,
    remind_time: datetime | None = None,
    venue: str | None = None,
    comment: str | None = None,
):
    """
    Создание записи на прием к психологу
    
    Args:
        patient_id: ID пациента
        therapist_id: ID психолога
        type: Тип консультации (онлайн/офлайн)
        scheduled_time: Время назначенной встречи
        reason: Причина обращения
        remind_time: Время напоминания
        venue: Место встречи (для онлайн)
        comment: Комментарий к записи
        
    Raises:
        PatientNotFoundException: Если пациент не найден
        TherapistNotFoundException: Если психолог не найден
        TherapistRoleNotFoundException: Если пользователь не имеет роли психолога
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

    therapist = await get_therapist_by_id(therapist_id)
    if therapist is None:
        raise exc.TherapistNotFoundException(therapist_id)


    match type:
        case AppointmentType.Offline:
            venue = therapist.office
        
        case AppointmentType.Online:
            if venue is None:
                raise exc.VenueRequiredException()

    return await repo_create_appointment(
        patient_id,
        therapist.user_id,
        type,
        reason,
        status,
        scheduled_time,
        remind_time,
        now,
        venue,
        comment,
    )


async def cancel_appointment_by_id(appointment_id: UUID):
    return await repo_cancel_appointment_by_id(appointment_id)


async def get_appointments_by_user_id(user_id: UUID):
    return await repo_get_appointments_by_user_id(user_id)


async def get_appointments_by_token(token: str):
    id = get_user_id_from_token(token)
    return await get_appointments_by_user_id(id)

