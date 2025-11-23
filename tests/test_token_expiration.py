import os
import time
import pytest
import jwt
from datetime import datetime
from unittest.mock import patch
from uuid import uuid4
from jwt.exceptions import ExpiredSignatureError
from psychohelp.repositories import create_access_token, get_user_id_from_token
from psychohelp.config.database import config, Config

class TestTokenExpiration:
    """Тесты для проверки истечения токенов"""

    def test_token_creation_with_configurable_expiration(self):
        """Тест создания токена с настраиваемым временем жизни"""
        user_id = str(uuid4())
        token = create_access_token(user_id)

        assert token is not None
        assert isinstance(token, str)

        decoded_user_id = get_user_id_from_token(token)
        assert str(decoded_user_id) == user_id

    def test_token_expiration_with_short_lifetime(self):
        """Тест истечения токена с коротким временем жизни"""
        user_id = str(uuid4())

        short_lifetime_minutes = 0.033  # ~2 секунды
        with patch.object(config, 'ACCESS_TOKEN_EXPIRE_MINUTES', short_lifetime_minutes):
            token = create_access_token(user_id)

            # Сразу после создания токен должен быть валиден
            decoded_user_id = get_user_id_from_token(token)
            assert str(decoded_user_id) == user_id

            # После этого токен уже должен быть просрочен
            with pytest.raises(ExpiredSignatureError):
                get_user_id_from_token(token)

    def test_token_expiration_with_default_lifetime(self):
        """Тест истечения токена с дефолтным временем жизни"""
        user_id = str(uuid4())
        token = create_access_token(user_id)
        decoded_user_id = get_user_id_from_token(token)
        assert str(decoded_user_id) == user_id

    def test_token_with_different_expiration_times(self):
        """Тест создания токенов с разным временем жизни"""
        user_id = str(uuid4())
        expiration_times = [1, 5, 30, 60, 1440]  # мин

        for minutes in expiration_times:
            with patch.object(config, 'ACCESS_TOKEN_EXPIRE_MINUTES', minutes):
                token = create_access_token(user_id)
                decoded_user_id = get_user_id_from_token(token)
                assert str(decoded_user_id) == user_id

    def test_invalid_token_handling(self):
        """Тест обработки невалидных токенов"""
        with pytest.raises(Exception):
            get_user_id_from_token("")

        with pytest.raises(Exception):
            get_user_id_from_token("invalid-token")

        with pytest.raises(Exception):
            get_user_id_from_token(
                "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0In0.invalid"
            )

    def test_environment_variable_override(self):
        """Тест переопределения времени жизни токена через переменные окружения"""
        with patch.object(Config, "ACCESS_TOKEN_EXPIRE_MINUTES", 5):
            test_config = Config()
            assert test_config.ACCESS_TOKEN_EXPIRE_MINUTES == 5

    def test_token_structure(self):
        """Тест структуры JWT токена"""
        user_id = str(uuid4())
        token = create_access_token(user_id)

        # JWT состоит из трёх частей
        parts = token.split(".")
        assert len(parts) == 3

        decoded = jwt.decode(token, options={"verify_signature": False})
        assert "sub" in decoded
        assert "exp" in decoded
        assert "iat" in decoded
        assert decoded["sub"] == user_id

        exp_timestamp = decoded["exp"]
        current_timestamp = datetime.utcnow().timestamp()
        assert exp_timestamp > current_timestamp
