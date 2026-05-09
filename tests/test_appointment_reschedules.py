from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

from psychohelp.models.appointment_reschedule_requests import (
    AppointmentRescheduleStatus,
)
from psychohelp.models.appointments import AppointmentStatus
from psychohelp.repositories import appointment_reschedule_requests as reschedule_repo
from psychohelp.services.appointments import appointments as appointments_service
from psychohelp.services.appointments import exceptions as appointment_exceptions


@pytest.mark.asyncio
async def test_request_appointment_reschedule_normalizes_and_delegates(monkeypatch):
    appointment_id = uuid4()
    psychologist_user_id = uuid4()
    scheduled_time = datetime.now(timezone.utc) + timedelta(days=1)
    remind_time = scheduled_time - timedelta(hours=1)
    captured = {}

    async def fake_create_reschedule_request(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(id=uuid4())

    monkeypatch.setattr(
        appointments_service.reschedule_repo,
        "create_reschedule_request",
        fake_create_reschedule_request,
    )

    result = await appointments_service.request_appointment_reschedule(
        appointment_id=appointment_id,
        psychologist_user_id=psychologist_user_id,
        scheduled_time=scheduled_time,
        remind_time=remind_time,
        venue="Кабинет 1",
        comment="Нужно перенести",
    )

    assert result.id
    assert captured["appointment_id"] == appointment_id
    assert captured["psychologist_user_id"] == psychologist_user_id
    assert captured["scheduled_time"].tzinfo == timezone.utc
    assert captured["remind_time"].tzinfo == timezone.utc
    assert captured["venue"] == "Кабинет 1"
    assert captured["comment"] == "Нужно перенести"


@pytest.mark.asyncio
async def test_request_appointment_reschedule_rejects_past_time(monkeypatch):
    async def fake_create_reschedule_request(**_kwargs):
        raise AssertionError("repository should not be called")

    monkeypatch.setattr(
        appointments_service.reschedule_repo,
        "create_reschedule_request",
        fake_create_reschedule_request,
    )

    with pytest.raises(appointment_exceptions.InvalidScheduledTimeException):
        await appointments_service.request_appointment_reschedule(
            appointment_id=uuid4(),
            psychologist_user_id=uuid4(),
            scheduled_time=datetime.now(timezone.utc) - timedelta(minutes=1),
        )


class FakeScalarResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class FakeSession:
    def __init__(self, result):
        self.result = result
        self.committed = False
        self.refreshed = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def execute(self, _query):
        return FakeScalarResult(self.result)

    async def commit(self):
        self.committed = True

    async def refresh(self, obj):
        self.refreshed = obj


class FakeDb:
    def __init__(self, session):
        self.session = session

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.mark.asyncio
async def test_confirm_reschedule_request_applies_changes(monkeypatch):
    patient_id = uuid4()
    new_time = datetime.now(timezone.utc) + timedelta(days=2)
    appointment = SimpleNamespace(
        patient_id=patient_id,
        status=AppointmentStatus.awaiting,
        scheduled_time=datetime.now(timezone.utc) + timedelta(days=1),
        remind_time=None,
        venue="Старый кабинет",
        comment="Старый комментарий",
        last_change_time=datetime.now(timezone.utc),
    )
    reschedule_request = SimpleNamespace(
        id=uuid4(),
        status=AppointmentRescheduleStatus.pending,
        appointment=appointment,
        requested_scheduled_time=new_time,
        requested_remind_time=None,
        requested_venue="Новый кабинет",
        requested_comment="Новый комментарий",
        responded_at=None,
    )
    session = FakeSession(reschedule_request)

    monkeypatch.setattr(reschedule_repo, "get_async_db", lambda: FakeDb(session))

    result = await reschedule_repo.confirm_reschedule_request(
        reschedule_request.id,
        patient_id,
    )

    assert result is reschedule_request
    assert session.committed is True
    assert appointment.scheduled_time == new_time
    assert appointment.venue == "Новый кабинет"
    assert appointment.comment == "Новый комментарий"
    assert reschedule_request.status == AppointmentRescheduleStatus.confirmed
    assert reschedule_request.responded_at is not None


@pytest.mark.asyncio
async def test_reject_reschedule_request_does_not_change_appointment(monkeypatch):
    patient_id = uuid4()
    old_time = datetime.now(timezone.utc) + timedelta(days=1)
    appointment = SimpleNamespace(
        patient_id=patient_id,
        status=AppointmentStatus.awaiting,
        scheduled_time=old_time,
        remind_time=None,
        venue="Старый кабинет",
        comment="Старый комментарий",
    )
    reschedule_request = SimpleNamespace(
        id=uuid4(),
        status=AppointmentRescheduleStatus.pending,
        appointment=appointment,
        rejection_comment=None,
        responded_at=None,
    )
    session = FakeSession(reschedule_request)

    monkeypatch.setattr(reschedule_repo, "get_async_db", lambda: FakeDb(session))

    result = await reschedule_repo.reject_reschedule_request(
        reschedule_request.id,
        patient_id,
        "Не подходит время",
    )

    assert result is reschedule_request
    assert session.committed is True
    assert appointment.scheduled_time == old_time
    assert appointment.venue == "Старый кабинет"
    assert appointment.comment == "Старый комментарий"
    assert reschedule_request.status == AppointmentRescheduleStatus.rejected
    assert reschedule_request.rejection_comment == "Не подходит время"
    assert reschedule_request.responded_at is not None


@pytest.mark.asyncio
async def test_reject_reschedule_request_forbids_non_patient(monkeypatch):
    appointment = SimpleNamespace(
        patient_id=uuid4(),
        status=AppointmentStatus.awaiting,
    )
    reschedule_request = SimpleNamespace(
        id=uuid4(),
        status=AppointmentRescheduleStatus.pending,
        appointment=appointment,
    )
    session = FakeSession(reschedule_request)

    monkeypatch.setattr(reschedule_repo, "get_async_db", lambda: FakeDb(session))

    with pytest.raises(PermissionError):
        await reschedule_repo.reject_reschedule_request(
            reschedule_request.id,
            uuid4(),
            "Не подходит время",
        )

    assert session.committed is False
