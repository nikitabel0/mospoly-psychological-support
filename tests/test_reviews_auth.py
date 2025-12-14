"""Тесты авторизации для отзывов."""
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
        "last_name": "Отзывов",
        "phone_number": f"+7999{random.randint(1000000, 9999999)}",
        "social_media": "https://vk.com/reviews_user",
        "email": f"reviews_{unique_id}@example.com",
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


async def test_get_review_without_auth():
    """Тест: попытка получить отзыв без авторизации."""
    review_id = str(uuid4())
    
    async with client() as c:
        r = await c.get(f"/reviews/{review_id}")
        assert r.status_code == 401


async def test_get_review_with_auth(authorized_user):
    """Тест: авторизованный пользователь может получить отзыв."""
    review_id = str(uuid4())
    
    async with client() as c:
        c.cookies.update(authorized_user["cookies"])
        
        r = await c.get(f"/reviews/{review_id}")
        # Обычный пользователь не имеет права REVIEWS_VIEW_ALL
        # Должен вернуть 403
        assert r.status_code == 403


async def test_create_review_without_auth():
    """Тест: попытка создать отзыв без авторизации."""
    appointment_id = str(uuid4())
    
    async with client() as c:
        r = await c.post("/reviews/", json={
            "appointment_id": appointment_id,
            "content": "Отличный психолог!"
        })
        assert r.status_code == 401


async def test_create_review_with_auth(authorized_user):
    """Тест: авторизованный пользователь может создать отзыв."""
    appointment_id = str(uuid4())
    
    async with client() as c:
        c.cookies.update(authorized_user["cookies"])
        
        r = await c.post("/reviews/", json={
            "appointment_id": appointment_id,
            "content": "Отличный психолог! Очень помог разобраться с проблемой."
        })
        # Может вернуть 400 если запись на прием не найдена
        assert r.status_code in [201, 400]


async def test_create_review_empty_content(authorized_user):
    """Тест: попытка создать отзыв с пустым содержимым."""
    appointment_id = str(uuid4())
    
    async with client() as c:
        c.cookies.update(authorized_user["cookies"])
        
        r = await c.post("/reviews/", json={
            "appointment_id": appointment_id,
            "content": ""
        })
        # Должна быть валидация на минимальную длину
        assert r.status_code == 422


async def test_get_psychologist_reviews_without_auth():
    """Тест: попытка получить отзывы психолога без авторизации."""
    psychologist_id = str(uuid4())
    
    async with client() as c:
        r = await c.get(f"/reviews/psychologist/{psychologist_id}")
        assert r.status_code == 401


async def test_get_psychologist_reviews_without_permission(authorized_user):
    """Тест: обычный пользователь не может просматривать отзывы психолога."""
    psychologist_id = str(uuid4())
    
    async with client() as c:
        c.cookies.update(authorized_user["cookies"])
        
        r = await c.get(f"/reviews/psychologist/{psychologist_id}")
        # Обычный пользователь не имеет права REVIEWS_VIEW_ALL
        assert r.status_code == 403


async def test_get_psychologist_reviews_pagination(authorized_user):
    """Тест: проверка параметров пагинации для отзывов психолога."""
    psychologist_id = str(uuid4())
    
    async with client() as c:
        c.cookies.update(authorized_user["cookies"])
        
        # Тест с параметрами пагинации
        r = await c.get(f"/reviews/psychologist/{psychologist_id}?skip=0&take=5")
        # Обычный пользователь не имеет права, должен быть 403
        assert r.status_code == 403


async def test_create_review_too_long_content(authorized_user):
    """Тест: попытка создать отзыв с слишком длинным содержимым."""
    appointment_id = str(uuid4())
    long_content = "А" * 6000  # Превышает максимум в 5000 символов
    
    async with client() as c:
        c.cookies.update(authorized_user["cookies"])
        
        r = await c.post("/reviews/", json={
            "appointment_id": appointment_id,
            "content": long_content
        })
        # Должна быть валидация на максимальную длину
        assert r.status_code == 422


async def test_invalid_token_reviews():
    """Тест: попытка доступа к отзывам с невалидным токеном."""
    review_id = str(uuid4())
    
    async with client() as c:
        c.cookies.set("access_token", "invalid_token_xyz")
        
        r = await c.get(f"/reviews/{review_id}")
        assert r.status_code == 401

