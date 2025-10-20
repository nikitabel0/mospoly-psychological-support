from datetime import datetime, timedelta, timezone

from fastapi import Response

from psychohelp.config import ACCESS_TOKEN_EXPIRE


def set_token_in_cookie(response: Response, token: str):
    response.set_cookie(
        key="access_token",
        value=token,
        expires=datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE),
        httponly=True,
        secure=True,
        samesite="None",
    )
