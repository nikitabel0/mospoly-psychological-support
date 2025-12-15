"""Тесты авторизации для просмотра психологов."""
import pytest
from uuid import uuid4
import random

from . import client


@pytest.fixture()
async def authorized_user():
    """Создать авторизованного пользователя."""
    unique_id = str(uuid4())
    data = {
        "first_name": "Авторизованный",
        "middle_name": "Юзерович",
        "last_name": "Пользователь",
        "phone_number": f"+7999{random.randint(1000000, 9999999)}",
        "social_media": "https://vk.com/authorized",
        "email": f"authorized_{unique_id}@example.com",
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


async def test_get_therapists_without_auth():
    """Тест: попытка получить список психологов без авторизации."""
    async with client() as c:
        r = await c.get("/therapists/")
        assert r.status_code == 401


async def test_get_therapists_with_auth(authorized_user):
    """Тест: авторизованный пользователь может просматривать список психологов."""
    async with client() as c:
        c.cookies.update(authorized_user["cookies"])
        
        r = await c.get("/therapists/")
        # Должен вернуть 200 (пустой список, если нет психологов)
        assert r.status_code == 200
        assert isinstance(r.json(), list)


async def test_get_therapist_by_id_without_auth():
    """Тест: попытка получить психолога по ID без авторизации."""
    from uuid import uuid4
    psychologist_id = str(uuid4())
    
    async with client() as c:
        r = await c.get(f"/therapists/{psychologist_id}")
        assert r.status_code == 401


async def test_get_therapist_by_id_with_auth(authorized_user):
    """Тест: авторизованный пользователь может просматривать психолога по ID."""
    from uuid import uuid4
    psychologist_id = str(uuid4())
    
    async with client() as c:
        c.cookies.update(authorized_user["cookies"])
        
        r = await c.get(f"/therapists/{psychologist_id}")
        # Должен вернуть 404 для несуществующего психолога
        assert r.status_code == 404


async def test_get_therapists_pagination(authorized_user):
    """Тест: проверка пагинации при получении списка психологов."""
    async with client() as c:
        c.cookies.update(authorized_user["cookies"])
        
        # Тест с параметрами пагинации
        r = await c.get("/therapists/?skip=0&take=5")
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        
        # Тест с невалидными параметрами
        r = await c.get("/therapists/?skip=-1&take=5")
        assert r.status_code == 422


async def test_create_therapist_without_permission(authorized_user):
    """Тест: обычный пользователь не может создать психолога."""
    from uuid import uuid4
    
    async with client() as c:
        c.cookies.update(authorized_user["cookies"])
        
        r = await c.post("/therapists/", json={
            "user_id": str(uuid4()),
            "experience": "5 лет опыта работы",
            "qualification": "Клинический психолог",
            "consult_areas": "Семейная терапия, тревожность",
            "description": "Специализируюсь на работе с семейными парами",
            "office": "Кабинет 301",
            "education": "МГУ, факультет психологии",
            "short_description": "Психолог с 5-летним опытом",
            "photo": None
        })
        assert r.status_code == 403


async def test_delete_therapist_without_permission(authorized_user):
    """Тест: обычный пользователь не может удалить психолога."""
    from uuid import uuid4
    psychologist_id = str(uuid4())
    
    async with client() as c:
        c.cookies.update(authorized_user["cookies"])
        
        r = await c.delete(f"/therapists/{psychologist_id}")
        assert r.status_code == 403

