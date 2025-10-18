from psychohelp.models.appointments import AppointmentStatus, AppointmentType
from psychohelp.models.roles import UserRole
from psychohelp.repositories import get_user_id_from_token
from psychohelp.repositories.appointments import (
    UUID,
    datetime,
)
from psychohelp.repositories.appointments import (
    cancel_appointment_by_id as repo_cancel_appointment_by_id,
)
from psychohelp.repositories.appointments import (
    create_appointment as repo_create_appointment,
)
from psychohelp.repositories.appointments import (
    get_appointment_by_id as repo_get_appointment_by_id,
)
from psychohelp.repositories.appointments import (
    get_appointments_by_user_id as repo_get_appointments_by_user_id,
)
from psychohelp.repositories.roles import get_roles_by_user_id
from psychohelp.repositories.therapists import get_therapist_by_id


async def get_appointment_by_id(appointment_id: UUID):
    return await repo_get_appointment_by_id(appointment_id)


async def create_appointment(
    patient_id: UUID,
    therapist_id: UUID,
    type: AppointmentType,
    reason: str | None = None,
    remind_time: datetime | None = None,
    venue: str | None = None,
):
    now = datetime.now()
    status = AppointmentStatus.Accepted

    roles = await get_roles_by_user_id(therapist_id)
    if UserRole.Therapist not in map(lambda r: r.role, roles):
        raise ValueError("Психолог не имеет соответствующей роли")

    # Встречаемся лично на месте работы психолога
    if type == AppointmentType.Offline:
        therapist = await get_therapist_by_id(therapist_id)
        if therapist is None:
            raise ValueError("Психолог не найден")
        venue = therapist.office

    elif venue is None:
        raise ValueError("Место для онлайн встречи не указано")

    return await repo_create_appointment(
        patient_id,
        therapist_id,
        type,
        reason,
        status,
        remind_time,
        now,
        venue,
    )


async def cancel_appointment_by_id(appointment_id: UUID):
    return await repo_cancel_appointment_by_id(appointment_id)


async def get_appointments_by_user_id(user_id: UUID):
    return await repo_get_appointments_by_user_id(user_id)


async def get_appointments_by_token(token: str):
    id = get_user_id_from_token(token)
    return await get_appointments_by_user_id(id)
