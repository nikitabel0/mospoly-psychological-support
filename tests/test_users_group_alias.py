from psychohelp.schemas.users import UserUpdateRequest


def test_user_update_request_accepts_group_alias():
    payload = {"group": "ИКБО-01-23"}
    data = UserUpdateRequest.model_validate(payload)

    assert data.study_group == "ИКБО-01-23"
    assert data.model_dump(exclude_unset=True)["study_group"] == "ИКБО-01-23"
