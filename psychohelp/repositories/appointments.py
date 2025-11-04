from psychohelp.models.appointments import (
    Appointment,
    AppointmentType,
    AppointmentStatus,
)
from psychohelp.config.database import get_async_db

from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from uuid import UUID
from datetime import datetime


async def get_appointment_by_id(appointment_id: UUID) -> Appointment | None:
    async with get_async_db() as session:
        result = await session.execute(
            select(Appointment).filter(Appointment.id == appointment_id)
        )
    return result.scalar_one_or_none()


async def create_appointment(
    patient_id: UUID,
    psychologist_id: UUID,
    type: AppointmentType,
    reason: str | None,
    status: AppointmentStatus,
    scheduled_time: datetime,
    remind_time: datetime | None,
    last_change_time: datetime,
    venue: str,
    comment: str | None = None,
) -> Appointment:
    async with get_async_db() as session:
        new_appointment = Appointment(
            patient_id=patient_id,
            psychologist_id=psychologist_id,
            type=type,
            reason=reason,
            status=status,
            scheduled_time=scheduled_time,
            remind_time=remind_time,
            last_change_time=last_change_time,
            venue=venue,
            comment=comment,
        )

        try:
            session.add(new_appointment)
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise

        return new_appointment


async def cancel_appointment_by_id(appointment_id: UUID) -> Appointment:
    async with get_async_db() as session:
        appointment = await session.execute(
            select(Appointment).filter(Appointment.id == appointment_id)
        )
        appointment = appointment.scalar_one_or_none()

        if appointment is None:
            raise ValueError("Встреча не найдена")

        if appointment.status == AppointmentStatus.Cancelled:
            raise ValueError("Встреча уже отменена")

        appointment.status = AppointmentStatus.Cancelled
        appointment.last_change_time = datetime.now()

        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise

        return appointment


async def get_appointments_by_user_id(user_id: UUID) -> list[Appointment]:
    async with get_async_db() as session:
        result = await session.execute(
            select(Appointment).filter(
                (Appointment.patient_id == user_id)
                | (Appointment.psychologist_id == user_id)
            )
        )
        return result.scalars().all()
