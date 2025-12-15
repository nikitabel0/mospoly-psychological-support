import pytest
import random

from . import client
from uuid import uuid4


async def test_get_user(user):
    """Тест получения пользователя по ID (требует авторизацию)."""
    async with client() as c:
        # Получаем токен из фикстуры user
        # Предполагаем, что фикстура возвращает cookies
        
        # Для получения своего профиля нужна авторизация
        # Сначала регистрируемся и логинимся
        unique_id = str(uuid4())
        data = {
            "first_name": "Тест",
            "middle_name": "Тестович",
            "last_name": "Тестов",
            "phone_number": f"+7999{random.randint(1000000, 9999999)}",
            "social_media": "https://vk.com/test",
            "email": f"test_{unique_id}@example.com",
            "password": "!qwerty123",
        }
        
        r = await c.post("/users/register", json=data)
        assert r.status_code == 201
        
        # Сохраняем cookies после регистрации
        c.cookies = dict(r.cookies)
        
        # Получаем данные пользователя
        r = await c.get("/users/user")
        assert r.status_code == 200
        user_id = r.json()["id"]
        
        # Теперь можем получить свой профиль по ID
        r = await c.get(f"/users/user/{user_id}")
        assert r.status_code == 200
        
        # Попытка получить несуществующего пользователя
        random_id = str(uuid4())
        r = await c.get(f"/users/user/{random_id}")
        # Должен вернуть 403 (нет прав) или 404 (не найден) в зависимости от логики
        assert r.status_code in [403, 404]


async def test_get_user_without_auth():
    """Тест получения пользователя без авторизации."""
    async with client() as c:
        user_id = str(uuid4())
        r = await c.get(f"/users/user/{user_id}")
        assert r.status_code == 401
