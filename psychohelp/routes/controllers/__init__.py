from fastapi import Response

from psychohelp.config import ACCESS_TOKEN_EXPIRE

from datetime import datetime, timezone, timedelta


def set_token_in_cookie(response: Response, token: str):
    response.set_cookie(
        key="access_token",
        value=token,
        expires=datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE),
        httponly=True,
        # fixme: поставил False в целях тестирования, потом нужно вернуть
        secure=False,
        # fixme: 
        # samesite="None",
    )
