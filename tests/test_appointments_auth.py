"""Тесты авторизации для записей на прием."""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4
import random

from . import client


@pytest.fixture()
async def user_one():
    """Создать первого пользователя."""
    unique_id = str(uuid4())
    data = {
        "first_name": "Первый",
        "middle_name": "Юзерович",
        "last_name": "Пользователь",
        "phone_number": f"+7999{random.randint(1000000, 9999999)}",
        "social_media": "https://vk.com/user1",
        "email": f"user1_{unique_id}@example.com",
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


@pytest.fixture()
async def user_two():
    """Создать второго пользователя."""
    unique_id = str(uuid4())
    data = {
        "first_name": "Второй",
        "middle_name": "Юзерович",
        "last_name": "Пользователь",
        "phone_number": f"+7999{random.randint(1000000, 9999999)}",
        "social_media": "https://vk.com/user2",
        "email": f"user2_{unique_id}@example.com",
        "password": "!qwerty456",
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


async def test_get_appointments_without_auth():
    """Тест: попытка получить записи без авторизации."""
    async with client() as c:
        r = await c.get("/appointments/")
        assert r.status_code == 401
        assert "не авторизован" in r.json()["detail"].lower()


async def test_get_own_appointments(user_one):
    """Тест: пользователь может получить свои записи."""
    async with client() as c:
        c.cookies.update(user_one["cookies"])
        
        r = await c.get("/appointments/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)


async def test_get_other_user_appointments_without_permission(user_one, user_two):
    """Тест: обычный пользователь не может просматривать записи другого пользователя."""
    async with client() as c:
        c.cookies.update(user_one["cookies"])
        
        # Попытка получить записи другого пользователя
        r = await c.get(f"/appointments/?user_id={user_two['id']}")
        assert r.status_code == 401  # Недостаточно прав
        assert "недостаточно прав" in r.json()["detail"].lower()


async def test_create_appointment_without_auth():
    """Тест: попытка создать запись без авторизации."""
    future_time = (datetime.utcnow() + timedelta(days=1)).isoformat()
    
    async with client() as c:
        r = await c.post("/appointments/create", json={
            "patient_id": str(uuid4()),
            "psychologist_id": str(uuid4()),
            "type": "Online",
            "scheduled_time": future_time,
            "venue": "https://meet.google.com/abc-defg-hij"
        })
        assert r.status_code == 401


async def test_create_appointment_with_auth(user_one):
    """Тест: авторизованный пользователь может создать запись."""
    future_time = (datetime.utcnow() + timedelta(days=1)).isoformat()
    
    async with client() as c:
        c.cookies.update(user_one["cookies"])
        
        r = await c.post("/appointments/create", json={
            "patient_id": user_one["id"],
            "psychologist_id": str(uuid4()),
            "type": "Online",
            "scheduled_time": future_time,
            "venue": "https://meet.google.com/abc-defg-hij"
        })
        # Может вернуть 404 если психолог не найден, но не 401/403
        assert r.status_code in [200, 201, 404, 422, 400]


async def test_get_appointment_by_id_without_auth():
    """Тест: попытка получить запись по ID без авторизации."""
    appointment_id = str(uuid4())
    
    async with client() as c:
        r = await c.get(f"/appointments/{appointment_id}")
        assert r.status_code == 401


async def test_get_appointment_by_id_with_auth(user_one):
    """Тест: авторизованный пользователь может получить запись по ID."""
    appointment_id = str(uuid4())
    
    async with client() as c:
        c.cookies.update(user_one["cookies"])
        
        r = await c.get(f"/appointments/{appointment_id}")
        # Должен вернуть 404 для несуществующей записи
        assert r.status_code == 404


async def test_cancel_appointment_without_auth():
    """Тест: попытка отменить запись без авторизации."""
    appointment_id = str(uuid4())
    
    async with client() as c:
        r = await c.put(f"/appointments/{appointment_id}/cancel")
        assert r.status_code == 401


async def test_cancel_appointment_with_auth(user_one):
    """Тест: авторизованный пользователь может отменить запись."""
    appointment_id = str(uuid4())
    
    async with client() as c:
        c.cookies.update(user_one["cookies"])
        
        r = await c.put(f"/appointments/{appointment_id}/cancel")
        # Может вернуть 400/404 для несуществующей записи
        assert r.status_code in [200, 400, 404]


async def test_invalid_token_appointments():
    """Тест: попытка доступа к записям с невалидным токеном."""
    async with client() as c:
        c.cookies.set("access_token", "invalid_token")
        
        r = await c.get("/appointments/")
        assert r.status_code == 401

