from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

from psychohelp.models.appointments import AppointmentType
from psychohelp.services.appointments import appointments as appointments_service


@pytest.mark.asyncio
async def test_create_appointment_accepts_psychologist_user_id(monkeypatch):
    patient_id = uuid4()
    psychologist_user_id = uuid4()
    psychologist_entity_id = uuid4()

    async def fake_get_user_by_id(user_id):
        if user_id == patient_id:
            return SimpleNamespace(
                id=patient_id,
                first_name="UserFirst",
                last_name="UserLast",
            )
        return None

    async def fake_get_application_by_id(_):
        return None

    async def fake_get_psychologist_by_id(psychologist_id):
        return None

    async def fake_get_psychologist_by_user_id(user_id):
        if user_id == psychologist_user_id:
            return SimpleNamespace(id=psychologist_entity_id, office="Office 101")
        return None

    async def fake_repo_create_appointment(
        patient_id,
        patient_first_name,
        patient_last_name,
        psychologist_id,
        type,
        reason,
        status,
        scheduled_time,
        remind_time,
        last_change_time,
        venue,
        application_id,
        comment,
    ):
        return SimpleNamespace(
            id=uuid4(),
            patient_id=patient_id,
            patient_first_name=patient_first_name,
            patient_last_name=patient_last_name,
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

    monkeypatch.setattr(appointments_service, "get_user_by_id", fake_get_user_by_id)
    monkeypatch.setattr(appointments_service, "get_application_by_id", fake_get_application_by_id)
    monkeypatch.setattr(appointments_service, "get_psychologist_by_id", fake_get_psychologist_by_id)
    monkeypatch.setattr(appointments_service, "get_psychologist_by_user_id", fake_get_psychologist_by_user_id)
    monkeypatch.setattr(appointments_service, "repo_create_appointment", fake_repo_create_appointment)

    appointment = await appointments_service.create_appointment(
        patient_id=patient_id,
        psychologist_id=psychologist_user_id,
        type=AppointmentType.Offline,
        scheduled_time=datetime.now(timezone.utc) + timedelta(hours=2),
        reason="test",
        comment="test",
    )

    assert appointment.psychologist_id == psychologist_entity_id
    assert appointment.venue == "Office 101"
    assert appointment.patient_first_name == "UserFirst"
    assert appointment.patient_last_name == "UserLast"


@pytest.mark.asyncio
async def test_create_appointment_copies_patient_name_from_application(monkeypatch):
    patient_id = uuid4()
    application_id = uuid4()
    psychologist_id = uuid4()

    async def fake_get_user_by_id(user_id):
        if user_id == patient_id:
            return SimpleNamespace(
                id=patient_id,
                first_name="ProfileFirst",
                last_name="ProfileLast",
            )
        return None

    async def fake_get_application_by_id(actual_application_id):
        assert actual_application_id == application_id
        return SimpleNamespace(
            id=application_id,
            first_name="ApplicationFirst",
            last_name="ApplicationLast",
        )

    async def fake_get_psychologist_by_id(actual_psychologist_id):
        if actual_psychologist_id == psychologist_id:
            return SimpleNamespace(id=psychologist_id, office="Office 101")
        return None

    async def fake_get_psychologist_by_user_id(_):
        return None

    async def fake_repo_create_appointment(
        patient_id,
        patient_first_name,
        patient_last_name,
        psychologist_id,
        type,
        reason,
        status,
        scheduled_time,
        remind_time,
        last_change_time,
        venue,
        application_id,
        comment,
    ):
        return SimpleNamespace(
            id=uuid4(),
            patient_id=patient_id,
            patient_first_name=patient_first_name,
            patient_last_name=patient_last_name,
            psychologist_id=psychologist_id,
            type=type,
            reason=reason,
            status=status,
            scheduled_time=scheduled_time,
            remind_time=remind_time,
            last_change_time=last_change_time,
            venue=venue,
            application_id=application_id,
            comment=comment,
        )

    async def fake_confirm_application(*args, **kwargs):
        return None

    monkeypatch.setattr(appointments_service, "get_user_by_id", fake_get_user_by_id)
    monkeypatch.setattr(appointments_service, "get_application_by_id", fake_get_application_by_id)
    monkeypatch.setattr(appointments_service, "get_psychologist_by_id", fake_get_psychologist_by_id)
    monkeypatch.setattr(appointments_service, "get_psychologist_by_user_id", fake_get_psychologist_by_user_id)
    monkeypatch.setattr(appointments_service, "repo_create_appointment", fake_repo_create_appointment)
    monkeypatch.setattr(appointments_service, "confirm_application", fake_confirm_application)

    appointment = await appointments_service.create_appointment(
        patient_id=patient_id,
        psychologist_id=psychologist_id,
        type=AppointmentType.Offline,
        scheduled_time=datetime.now(timezone.utc) + timedelta(hours=2),
        application_id=application_id,
    )

    assert appointment.patient_first_name == "ApplicationFirst"
    assert appointment.patient_last_name == "ApplicationLast"
    assert appointment.application_id == application_id
