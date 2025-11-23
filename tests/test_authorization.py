"""Тесты базовой авторизации и прав доступа."""
import pytest
from uuid import uuid4
import random

from . import client


@pytest.fixture()
async def regular_user():
    """Создать обычного пользователя (роль USER)."""
    unique_id = str(uuid4())
    data = {
        "first_name": "Иван",
        "middle_name": "Иванович",
        "last_name": "Петров",
        "phone_number": f"+7999{random.randint(1000000, 9999999)}",
        "social_media": "https://vk.com/user1",
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


@pytest.fixture()
async def second_user():
    """Создать второго обычного пользователя."""
    unique_id = str(uuid4())
    data = {
        "first_name": "Мария",
        "middle_name": "Петровна",
        "last_name": "Сидорова",
        "phone_number": f"+7999{random.randint(1000000, 9999999)}",
        "social_media": "https://vk.com/user2",
        "email": f"second_{unique_id}@example.com",
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


@pytest.fixture()
async def admin_user(regular_user):
    """Создать администратора (присвоив роль ADMIN существующему пользователю)."""
    # Note: В реальном тесте нужно будет использовать прямую вставку в БД
    # или создать специальный эндпоинт для тестов
    # Пока возвращаем обычного пользователя сометкой, что это админ
    admin_data = regular_user.copy()
    admin_data["is_admin"] = True
    return admin_data


async def test_unauthorized_access():
    """Тест доступа без авторизации к защищенным эндпоинтам."""
    async with client() as c:
        # Попытка получить свой профиль без авторизации
        r = await c.get("/users/user")
        assert r.status_code == 401
        assert "не авторизован" in r.json()["detail"].lower()


async def test_invalid_token():
    """Тест доступа с невалидным токеном."""
    async with client() as c:
        c.cookies.set("access_token", "invalid_token_123")
        
        # Попытка получить свой профиль с невалидным токеном
        r = await c.get("/users/user")
        assert r.status_code == 401


async def test_user_can_view_own_profile(regular_user):
    """Тест: пользователь может просматривать свой профиль."""
    async with client() as c:
        c.cookies.update(regular_user["cookies"])
        
        r = await c.get(f"/users/user/{regular_user['id']}")
        assert r.status_code == 200
        assert r.json()["id"] == regular_user["id"]


async def test_user_cannot_view_other_profile(regular_user, second_user):
    """Тест: обычный пользователь не может просматривать чужие профили."""
    async with client() as c:
        c.cookies.update(regular_user["cookies"])
        
        # Попытка просмотреть профиль другого пользователя
        r = await c.get(f"/users/user/{second_user['id']}")
        assert r.status_code == 403
        assert "недостаточно прав" in r.json()["detail"].lower()


async def test_logout(regular_user):
    """Тест выхода из системы."""
    async with client() as c:
        c.cookies.update(regular_user["cookies"])
        
        # Проверяем, что авторизованы
        r = await c.get("/users/user")
        assert r.status_code == 200
        
        # Выходим
        r = await c.post("/users/logout")
        assert r.status_code == 200
        
        # Обновляем cookies после логаута
        c.cookies = dict(r.cookies)
        
        # Проверяем, что больше не авторизованы
        r = await c.get("/users/user")
        assert r.status_code == 401


async def test_login(regular_user):
    """Тест входа в систему с существующими данными."""
    async with client() as c:
        # Вход с правильными данными (используем email из фикстуры)
        r = await c.post("/users/login", json={
            "email": regular_user["email"],
            "password": "!qwerty123"
        })
        assert r.status_code == 200
        assert r.json()["email"] == regular_user["email"]
        
        # Проверяем, что токен установлен
        assert "access_token" in r.cookies


async def test_login_wrong_password():
    """Тест входа с неверным паролем."""
    # Сначала создаем пользователя
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

    async with client() as c:
        r_reg = await c.post("/users/register", json=data)
        assert r_reg.status_code == 201
        
        # Попытка входа с неверным паролем
        r = await c.post("/users/login", json={
            "email": data["email"],
            "password": "wrong_password"
        })
        assert r.status_code == 403
        assert "неверные данные" in r.json()["detail"].lower()

