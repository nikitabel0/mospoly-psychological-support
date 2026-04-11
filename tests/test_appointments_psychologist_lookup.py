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
            return SimpleNamespace(id=patient_id)
        return None

    async def fake_get_psychologist_by_id(psychologist_id):
        return None

    async def fake_get_psychologist_by_user_id(user_id):
        if user_id == psychologist_user_id:
            return SimpleNamespace(id=psychologist_entity_id, office="Office 101")
        return None

    async def fake_repo_create_appointment(
        patient_id,
        psychologist_id,
        type,
        reason,
        status,
        scheduled_time,
        remind_time,
        last_change_time,
        venue,
        comment,
    ):
        return SimpleNamespace(
            id=uuid4(),
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

    monkeypatch.setattr(appointments_service, "get_user_by_id", fake_get_user_by_id)
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
