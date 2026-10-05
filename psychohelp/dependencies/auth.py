from fastapi import Request, HTTPException
from jwt.exceptions import PyJWTError
from starlette.status import HTTP_401_UNAUTHORIZED
from psychohelp.services.users.users import get_user_by_token
from psychohelp.models.users import User


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Пользователь не авторизован",
    )


async def get_current_user(request: Request) -> User:
    """Dependency для получения текущего пользователя из токена"""
    token = request.cookies.get("access_token")
    if not token:
        raise _unauthorized()

    try:
        user = await get_user_by_token(token)
    except (PyJWTError, KeyError, ValueError):
        raise _unauthorized()

    if user is None:
        raise _unauthorized()

    return user


async def get_optional_user(request: Request) -> User | None:
    """Dependency для опционального получения пользователя (если токен есть)"""
    token = request.cookies.get("access_token")
    if not token:
        return None

    try:
        user = await get_user_by_token(token)
    except (PyJWTError, KeyError, ValueError):
        raise _unauthorized()

    if user is None:
        raise _unauthorized()

    return user
