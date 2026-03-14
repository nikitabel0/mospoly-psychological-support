from fastapi import Response

from psychohelp.config.config import config

from datetime import datetime, timezone, timedelta


def set_token_in_cookie(response: Response, token: str):
    response.set_cookie(
        key="access_token",
        value=token,
        expires=datetime.now(timezone.utc) + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES),
        httponly=True,  # Защита от XSS
        secure=False,   # False для HTTP, True для HTTPS
        samesite="None",  # Для cross-site запросов (работает с secure=False на некоторых браузерах в dev режиме)
    )

def set_refresh_token_in_cookie(response: Response, refresh_token: str):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        expires=datetime.now(timezone.utc) + timedelta(minutes=config.REFRESH_TOKEN_EXPIRE),
        httponly=True,  # Защита от XSS
        secure=False,   # False для HTTP, True для HTTPS
        samesite="None",  # Для cross-site запросов (работает с secure=False на некоторых браузерах в dev режиме)
    )
