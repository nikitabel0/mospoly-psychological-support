from types import SimpleNamespace
from uuid import uuid4

import pytest

from psychohelp.models.appointments import AppointmentStatus
from psychohelp.repositories import appointments as appointments_repo
from psychohelp.schemas.appointments import AppointmentBase, AppointmentDoneRequest


class FakeScalarResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class FakeSession:
    def __init__(self, appointment):
        self.appointment = appointment
        self.committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def execute(self, _query):
        return FakeScalarResult(self.appointment)

    async def commit(self):
        self.committed = True

    async def rollback(self):
        pass


class FakeDb:
    def __init__(self, session):
        self.session = session

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.mark.asyncio
async def test_complete_appointment_stores_patient_and_psychologist_comments(monkeypatch):
    psychologist_user_id = uuid4()
    appointment = SimpleNamespace(
        id=uuid4(),
        psychologist=SimpleNamespace(user_id=psychologist_user_id),
        status=AppointmentStatus.awaiting,
        conclusion=None,
        psychologist_comment=None,
        last_change_time=None,
    )
    session = FakeSession(appointment)

    monkeypatch.setattr(appointments_repo, "get_async_db", lambda: FakeDb(session))

    result = await appointments_repo.complete_appointment_by_psychologist(
        appointment.id,
        psychologist_user_id,
        "Комментарий пациенту",
        "Комментарий психологам",
    )

    assert result is appointment
    assert session.committed is True
    assert appointment.status == AppointmentStatus.done
    assert appointment.conclusion == "Комментарий пациенту"
    assert appointment.psychologist_comment == "Комментарий психологам"
    assert appointment.last_change_time is not None


def test_appointment_done_request_accepts_legacy_conclusion_alias():
    request = AppointmentDoneRequest.model_validate(
        {
            "conclusion": "Старое поле для пациента",
            "psychologist_comment": "Внутренняя заметка",
        }
    )

    assert request.patient_comment == "Старое поле для пациента"
    assert request.psychologist_comment == "Внутренняя заметка"


def test_internal_psychologist_comment_is_not_in_shared_appointment_response():
    assert "psychologist_comment" not in AppointmentBase.model_fields
