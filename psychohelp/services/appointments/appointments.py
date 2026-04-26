from datetime import datetime, timezone
from uuid import UUID

from psychohelp.repositories import get_user_id_from_token
from psychohelp.repositories.appointments import (
    get_appointment_by_id as repo_get_appointment_by_id,
    create_appointment as repo_create_appointment,
    cancel_appointment_by_id as repo_cancel_appointment_by_id,
    get_appointments_by_user_id as repo_get_appointments_by_user_id,
)
from psychohelp.repositories.applications import get_application_by_id
from psychohelp.repositories.psychologists.psychologists import (
    get_psychologist_by_id,
    get_psychologist_by_user_id,
)
from psychohelp.repositories.users import get_user_by_id
from psychohelp.models.appointments import Appointment, AppointmentType, AppointmentStatus
from psychohelp.services.appointments import exceptions as exc
from psychohelp.services.applications.applications import confirm_application


async def get_appointment_by_id(appointment_id: UUID, user_id: UUID) -> Appointment | None:
    return await repo_get_appointment_by_id(appointment_id, user_id)


async def create_appointment(
    patient_id: UUID,
    psychologist_id: UUID,
    type: AppointmentType,
    scheduled_time: datetime,
    reason: str | None = None,
    remind_time: datetime | None = None,
    venue: str | None = None,
    comment: str | None = None,
    application_id: UUID | None = None,
) -> Appointment:
    now = datetime.now(timezone.utc)
    status = AppointmentStatus.awaiting

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

    # Проверка существования заявки
    if application_id:
        application = await get_application_by_id(application_id)
        if application is None:
            raise exc.ApplicationNotFoundException(application_id)

    psychologist = await get_psychologist_by_id(psychologist_id)
    if psychologist is None:
        psychologist = await get_psychologist_by_user_id(psychologist_id)
    if psychologist is None:
        raise exc.PsychologistNotFoundException(psychologist_id)

    match type:
        case AppointmentType.Offline:
            venue = psychologist.office
        case AppointmentType.Online:
            if venue is None:
                raise exc.VenueRequiredException()

    appointment = await repo_create_appointment(
        patient_id=patient_id,
        psychologist_id=psychologist.id,
        application_id=application_id,
        type=type,
        reason=reason,
        status=status,
        scheduled_time=scheduled_time,
        remind_time=remind_time,
        last_change_time=now,
        venue=venue,
        comment=comment,
    )

    if application_id:
        await confirm_application(
            application_id=application_id,
            appointment_id=appointment.id,
            actor_id=patient_id,
            is_owner=True
        )
        
    # Возвращаем полностью подгруженный объект
    return await repo_get_appointment_by_id(appointment.id, patient_id)


async def cancel_appointment_by_id(appointment_id: UUID) -> Appointment:
    # Этот метод скорее всего не используется напрямую из контроллеров без user_id
    # Оставляем как есть, если он где-то нужен внутри системных сервисов
    return await repo_cancel_appointment_by_id(appointment_id)


async def get_appointments_by_user_id(user_id: UUID) -> list[Appointment]:
    return await repo_get_appointments_by_user_id(user_id)


async def get_appointments_by_token(token: str) -> list[Appointment]:
    user_id = get_user_id_from_token(token)
    return await get_appointments_by_user_id(user_id)


async def cancel_appointment_by_patient(appointment_id: UUID, patient_id: UUID, cancel_reason: str) -> Appointment:
    from psychohelp.repositories.appointments import cancel_appointment_by_id as repo_cancel
    appointment = await repo_cancel(appointment_id, patient_id, cancel_reason)
    return appointment


async def get_appointment_for_user(appointment_id: UUID, user_id: UUID) -> Appointment | None:
    from psychohelp.repositories.appointments import get_appointment_for_user as repo_get
    appointment = await repo_get(appointment_id, user_id)
    return appointment


async def complete_appointment(
        appointment_id: UUID,
        psychologist_id: UUID,
        conclusion: str) -> Appointment:
    from psychohelp.repositories.appointments import complete_appointment_by_psychologist as repo_complete
    appointment = await repo_complete(appointment_id, psychologist_id, conclusion)
    return appointment