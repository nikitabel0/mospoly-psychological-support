from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from psychohelp.constants.rbac import RoleCode
from psychohelp.routes.controllers import roles as roles_controller
from psychohelp.schemas.roles import RoleAssignRequest, RoleRemoveRequest


@pytest.mark.asyncio
async def test_assign_role_allows_admin_role(monkeypatch):
    current_user_id = uuid4()
    target_user_id = uuid4()

    async def fake_assign_role_to_user(user_id, role_code):
        assert user_id == target_user_id
        assert role_code == RoleCode.PSYCHOLOGIST
        return True

    monkeypatch.setattr(roles_controller, "assign_role_to_user", fake_assign_role_to_user)

    result = await roles_controller.assign_role(
        target_user_id,
        RoleAssignRequest(role_code=RoleCode.PSYCHOLOGIST),
        current_user=SimpleNamespace(
            id=current_user_id,
            roles=[SimpleNamespace(code=RoleCode.ADMIN)],
        ),
    )

    assert result == {"message": "Роль 'psychologist' успешно назначена"}


@pytest.mark.asyncio
async def test_assign_role_forbids_non_admin_role(monkeypatch):
    async def fake_assign_role_to_user(_user_id, _role_code):
        raise AssertionError("role should not be assigned")

    monkeypatch.setattr(roles_controller, "assign_role_to_user", fake_assign_role_to_user)

    with pytest.raises(HTTPException) as exc:
        await roles_controller.assign_role(
            uuid4(),
            RoleAssignRequest(role_code=RoleCode.PSYCHOLOGIST),
            current_user=SimpleNamespace(
                id=uuid4(),
                roles=[SimpleNamespace(code=RoleCode.USER)],
            ),
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == "Только для администраторов"


@pytest.mark.asyncio
async def test_remove_role_allows_admin_role(monkeypatch):
    current_user_id = uuid4()
    target_user_id = uuid4()

    async def fake_remove_role_from_user(user_id, role_code):
        assert user_id == target_user_id
        assert role_code == RoleCode.PSYCHOLOGIST
        return True

    monkeypatch.setattr(roles_controller, "remove_role_from_user", fake_remove_role_from_user)

    result = await roles_controller.remove_role(
        target_user_id,
        RoleRemoveRequest(role_code=RoleCode.PSYCHOLOGIST),
        current_user=SimpleNamespace(
            id=current_user_id,
            roles=[SimpleNamespace(code=RoleCode.ADMIN)],
        ),
    )

    assert result == {"message": "Роль 'psychologist' успешно удалена"}
