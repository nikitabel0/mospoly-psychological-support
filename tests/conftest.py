import os
import pytest
from uuid import uuid4
import random

import psycopg2

from . import client


@pytest.fixture()
async def user():
    # Генерируем уникальный email для каждого теста
    unique_id = str(uuid4())
    data = {
        "first_name": "Иван",
        "middle_name": "Иванович",
        "last_name": "Иванов",
        "phone_number": f"+7999{random.randint(1000000, 9999999)}",  # Уникальный номер (только цифры)
        "social_media": "https://example.com",
        "email": f"user_{unique_id}@example.com",
        "password": "!qwerty123",
    }

    async with client() as c:
        r = await c.post("/users/register", json=data)
        assert r.status_code == 201
        
        # Сохраняем cookies сразу после регистрации
        saved_cookies = dict(r.cookies)

        r = await c.get("/users/user")
        assert r.status_code == 200
        
        user_data = r.json()

    user_data["cookies"] = saved_cookies
    return user_data


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_users():
    """Очистить тестовых пользователей перед всеми тестами."""
    # Код выполняется ДО всех тестов - очищаем БД
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "db"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            database=os.getenv("POSTGRES_DB", "postgres"),
        )
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE email LIKE '%@example.com';")
        conn.close()
    except Exception:
        # Игнорируем любые ошибки при очистке
        pass
    yield
