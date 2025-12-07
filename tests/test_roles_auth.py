"""Тесты авторизации для управления ролями."""
import pytest
from uuid import uuid4
import random

from . import client


@pytest.fixture()
async def regular_user():
    """Создать обычного пользователя."""
    unique_id = str(uuid4())
    data = {
        "first_name": "Обычный",
        "middle_name": "Юзерович",
        "last_name": "Пользователь",
        "phone_number": f"+7999{random.randint(1000000, 9999999)}",
        "social_media": "https://vk.com/regular",
        "email": f"regular_{unique_id}@example.com",
        "password": "!qwerty123",
    }

    async with client() as c:
        r = await c.post("/users/register", json=data)
        assert r.status_code == 201
        
        saved_cookies = dict(r.cookies)

        r = await c.get("/users/user")
        assert r.status_code == 200
        
        user_data = r.json()

    user_data["cookies"] = saved_cookies
    return user_data


async def test_assign_role_without_auth():
    """Тест: попытка назначить роль без авторизации."""
    user_id = str(uuid4())
    
    async with client() as c:
        r = await c.post(f"/roles/{user_id}/assign", json={
            "role_code": "psychologist"
        })
        assert r.status_code == 401


async def test_assign_role_without_permission(regular_user):
    """Тест: обычный пользователь не может назначать роли."""
    user_id = str(uuid4())
    
    async with client() as c:
        c.cookies.update(regular_user["cookies"])
        
        r = await c.post(f"/roles/{user_id}/assign", json={
            "role_code": "psychologist"
        })
        assert r.status_code == 403
        assert "недостаточно прав" in r.json()["detail"].lower()


async def test_remove_role_without_auth():
    """Тест: попытка удалить роль без авторизации."""
    user_id = str(uuid4())
    
    async with client() as c:
        r = await c.post(f"/roles/{user_id}/remove", json={
            "role_code": "user"
        })
        assert r.status_code == 401


async def test_remove_role_without_permission(regular_user):
    """Тест: обычный пользователь не может удалять роли."""
    user_id = str(uuid4())
    
    async with client() as c:
        c.cookies.update(regular_user["cookies"])
        
        r = await c.post(f"/roles/{user_id}/remove", json={
            "role_code": "user"
        })
        assert r.status_code == 403
        assert "недостаточно прав" in r.json()["detail"].lower()


async def test_assign_role_nonexistent_user(regular_user):
    """Тест: назначение роли несуществующему пользователю."""
    # Для этого теста нужен админ, но пока проверим только формат запроса
    nonexistent_user_id = str(uuid4())
    
    async with client() as c:
        c.cookies.update(regular_user["cookies"])
        
        r = await c.post(f"/roles/{nonexistent_user_id}/assign", json={
            "role_code": "psychologist"
        })
        # Должен вернуть 403, так как у пользователя нет прав
        assert r.status_code == 403

