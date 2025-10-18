import pytest

from . import client


@pytest.fixture()
async def user():
    data = {
        "first_name": "Иван",
        "middle_name": "Иванов",
        "last_name": "Иванович",
        "phone_number": "+79991234567",
        "social_media": "https://example.com",
        "email": "user@example.com",
        "password": "!qwerty123",
    }

    async with client() as c:
        r = await c.post("/users/register", json=data)
        assert r.status_code == 201

        c.cookies = dict(r.cookies)
        r = await c.get("/users/user")
        assert r.status_code == 200

    return r.json()
