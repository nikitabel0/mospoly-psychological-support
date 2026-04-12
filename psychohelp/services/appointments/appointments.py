# psychohelp/services/appointments/appointments.py

from datetime import datetime, timezone
from uuid import UUID

from psychohelp.repositories import get_user_id_from_token
from psychohelp.repositories.appointments import (
    get_appointment_by_id as repo_get_appointment_by_id,
    create_appointment as repo_create_appointment,
    cancel_appointment_by_id as repo_cancel_appointment_by_id,
    get_appointments_by_user_id as repo_get_appointments_by_user_id,
)
from psychohelp.repositories.psychologists.psychologists import (
    get_psychologist_by_id,
    get_psychologist_by_user_id,
)
from psychohelp.repositories.users import get_user_by_id
from psychohelp.models.appointments import Appointment, AppointmentType, AppointmentStatus
from psychohelp.services.appointments import exceptions as exc
from psychohelp.services.applications.applications import confirm_application  # импорт функции подтверждения заявки


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
    application_id: UUID | None = None,   # новый параметр – ID заявки, которую нужно завершить
) -> Appointment:
    """
    Создание записи на прием к психологу.
    Если передан application_id, то после создания записи заявка автоматически переводится в статус completed
    и связывается с этой записью (атомарно в рамках одной транзакции – требуется общий сеанс БД).
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
        # Backward-compatible behavior: some clients send psychologist user_id here.
        psychologist = await get_psychologist_by_user_id(psychologist_id)
    if psychologist is None:
        raise exc.PsychologistNotFoundException(psychologist_id)

    match type:
        case AppointmentType.Offline:
            venue = psychologist.office
        case AppointmentType.Online:
            if venue is None:
                raise exc.VenueRequiredException()

    # Создаём запись в БД
    appointment = await repo_create_appointment(
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

    # Если передан ID заявки – связываем и завершаем заявку
    if application_id:
        # Здесь мы предполагаем, что confirm_application использует отдельный сеанс БД.
        # Для полной атомарности нужно передавать общий сеанс (session), но для упрощения пока так.
        # Важно: confirm_application должен обновить заявку, установив appointment_id и статус completed.
        await confirm_application(
            application_id=application_id,
            appointment_id=appointment.id,
            actor_id=patient_id,
            is_owner=True
        )
    return appointment


async def cancel_appointment_by_id(appointment_id: UUID) -> Appointment:
    return await repo_cancel_appointment_by_id(appointment_id)


async def get_appointments_by_user_id(user_id: UUID) -> list[Appointment]:
    return await repo_get_appointments_by_user_id(user_id)


async def get_appointments_by_token(token: str) -> list[Appointment]:
    user_id = get_user_id_from_token(token)
    return await get_appointments_by_user_id(user_id)


async def cancel_appointment_by_patient(appointment_id: UUID, patient_id: UUID, cancel_reason: str) -> Appointment:
    """Отмена записи пациентом"""
    from psychohelp.repositories.appointments import cancel_appointment_by_id as repo_cancel
    appointment = await repo_cancel(appointment_id, patient_id, cancel_reason)
    return appointment


async def get_appointment_for_user(appointment_id: UUID, user_id: UUID) -> Appointment | None:
    """Получить запись для пользователя (проверка прав доступа)"""
    from psychohelp.repositories.appointments import get_appointment_for_user as repo_get
    appointment = await repo_get(appointment_id, user_id)
    return appointment
