from psychohelp.models.appointments import (
    Appointment,
    AppointmentType,
    AppointmentStatus,
)

from psychohelp.models.psychologists import Psychologist
from psychohelp.models.appointments import Appointment
from psychohelp.config.config import get_async_db

from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from uuid import UUID
from datetime import datetime, timezone


async def get_appointment_by_id(appointment_id: UUID, user_id: UUID) -> Appointment | None:
    """Получить запись по ID с проверкой прав доступа (пациент или психолог)"""
    async with get_async_db() as session:
        query = select(Appointment).filter(
            Appointment.id == appointment_id,
            (
                (Appointment.patient_id == user_id) | 
                Appointment.psychologist.has(Psychologist.user_id == user_id)
            )
        )
        
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def create_appointment(
    patient_id: UUID,
    patient_first_name: str,
    patient_last_name: str,
    psychologist_id: UUID,
    type: AppointmentType,
    reason: str | None,
    status: AppointmentStatus,
    scheduled_time: datetime,
    remind_time: datetime | None,
    last_change_time: datetime,
    venue: str,
    application_id: UUID | None = None,
    comment: str | None = None,
) -> Appointment:
    async with get_async_db() as session:
        new_appointment = Appointment(
            patient_id=patient_id,
            patient_first_name=patient_first_name,
            patient_last_name=patient_last_name,
            psychologist_id=psychologist_id,
            application_id=application_id,
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
            await session.refresh(new_appointment)
        except IntegrityError:
            await session.rollback()
            raise

        return new_appointment


async def cancel_appointment_by_id(appointment_id: UUID, current_user_id: UUID, cancel_reason: str) -> Appointment:
    async with get_async_db() as session:
        appointment = await session.execute(
            select(Appointment).filter(Appointment.id == appointment_id)
        )
        appointment = appointment.scalar_one_or_none()

        if appointment is None:
            raise ValueError("Встреча не найдена")

        if appointment.patient_id != current_user_id:
            raise ValueError("Только пациент может отменить свою запись")

        if appointment.status == AppointmentStatus.cancelled:
            raise ValueError("Встреча уже отменена")

        appointment.status = AppointmentStatus.cancelled
        appointment.cancel_reason = cancel_reason
        appointment.last_change_time = datetime.now(timezone.utc)

        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise

        return appointment


async def get_appointments_by_user_id(user_id: UUID) -> list[Appointment]:
    async with get_async_db() as session:
        query = (
            select(Appointment)
            # Присоединяем таблицу психологов по ключу
            .outerjoin(Psychologist, Appointment.psychologist_id == Psychologist.id)
            .filter(
                (Appointment.patient_id == user_id) | 
                (Psychologist.user_id == user_id) # Теперь сравниваем с нужным полем
            )
        )
        
        result = await session.execute(query)
        return result.scalars().all()

async def complete_appointment_by_psychologist(
        appointment_id: UUID,
        psychologist_id: UUID,
        conclusion: str) -> Appointment:
    async with get_async_db() as session:
        appointment = await session.execute(
            select(Appointment).filter(Appointment.id == appointment_id))
        appointment = appointment.scalar_one_or_none()

        if appointment is None:
            raise ValueError("Встреча не найдена")
        if appointment.psychologist_id != psychologist_id:
            raise PermissionError("Только назначенный психолог может завершить прием")
        if appointment.status in (AppointmentStatus.done, AppointmentStatus.cancelled):
            raise ValueError("Нельзя завершить эту встречу (она уже завершена или отменена)")

        appointment.status = AppointmentStatus.done
        appointment.conclusion = conclusion
        appointment.last_change_time = datetime.now(timezone.utc)

        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise

        return appointment
