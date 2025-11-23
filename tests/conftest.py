import pytest
from uuid import uuid4
import subprocess
import random

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


@pytest.fixture(scope="function", autouse=True)
def cleanup_test_users():
    """Очистить тестовых пользователей после каждого теста."""
    # Код выполняется ДО теста
    yield
    # Код выполняется ПОСЛЕ теста - очищаем БД
    try:
        subprocess.run(
            [
                "docker-compose", "exec", "-T", "db",
                "psql", "-U", "myuser", "-d", "mydatabase",
                "-c", "DELETE FROM users WHERE email LIKE '%@example.com';"
            ],
            capture_output=True,
            timeout=5,
            check=False  # Не падаем если команда не удалась
        )
    except Exception:
        # Игнорируем любые ошибки при очистке
        pass
