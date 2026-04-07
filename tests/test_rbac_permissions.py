import pytest
from uuid import uuid4

from fastapi import HTTPException

from psychohelp.constants.rbac import PermissionCode
from psychohelp.services.rbac.permissions import require_permission
import psychohelp.services.rbac.permissions as permissions_module


class DummyUser:
    def __init__(self, user_id):
        self.id = user_id


@pytest.mark.asyncio
async def test_require_permission_uses_current_user_without_request(monkeypatch):
    user_id = uuid4()

    async def fake_has_permission(actual_user_id, permission_code):
        assert actual_user_id == user_id
        assert permission_code == PermissionCode.APPOINTMENTS_CREATE_OWN
        return True

    monkeypatch.setattr(permissions_module, "user_has_permission", fake_has_permission)

    @require_permission(PermissionCode.APPOINTMENTS_CREATE_OWN)
    async def protected_endpoint(current_user):
        return {"ok": True}

    result = await protected_endpoint(current_user=DummyUser(user_id))
    assert result == {"ok": True}


@pytest.mark.asyncio
async def test_require_permission_without_request_and_user_returns_401(monkeypatch):
    async def fake_has_permission(actual_user_id, permission_code):
        return True

    monkeypatch.setattr(permissions_module, "user_has_permission", fake_has_permission)

    @require_permission(PermissionCode.APPOINTMENTS_CREATE_OWN)
    async def protected_endpoint():
        return {"ok": True}

    with pytest.raises(HTTPException) as exc:
        await protected_endpoint()

    assert exc.value.status_code == 401
    assert exc.value.detail == "Не авторизован"
