from uuid import UUID
from functools import wraps

from fastapi import HTTPException, Request
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED

from psychohelp.repositories import get_user_id_from_token
from psychohelp.repositories.rbac.rbac import (
    get_user_permissions as repo_get_user_permissions,
)
from psychohelp.constants.rbac import PermissionCode


async def get_user_permissions(user_id: UUID) -> list[str]:
    """Return all permission codes granted to user via roles."""
    return await repo_get_user_permissions(user_id)


async def user_has_permission(user_id: UUID, permission_code: PermissionCode) -> bool:
    """Check whether user has a specific permission."""
    permissions = await get_user_permissions(user_id)
    return permission_code.value in permissions


async def user_has_any_permission(user_id: UUID, permission_codes: list[PermissionCode]) -> bool:
    """Check whether user has at least one permission from a list."""
    permissions = await get_user_permissions(user_id)
    return any(code.value in permissions for code in permission_codes)


def require_permission(permission_code: PermissionCode):
    """Decorator that enforces RBAC permission checks."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request")
            current_user = kwargs.get("current_user")

            if request is None:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if current_user is not None and getattr(current_user, "id", None):
                user_id = current_user.id
            else:
                if request is None:
                    raise HTTPException(
                        status_code=HTTP_401_UNAUTHORIZED,
                        detail="Не авторизован",
                    )

                token = request.cookies.get("access_token")
                if not token:
                    raise HTTPException(
                        status_code=HTTP_401_UNAUTHORIZED,
                        detail="Не авторизован",
                    )

                try:
                    user_id = get_user_id_from_token(token)
                except Exception:
                    raise HTTPException(
                        status_code=HTTP_401_UNAUTHORIZED,
                        detail="Невалидный токен",
                    )

            has_permission = await user_has_permission(user_id, permission_code)
            if not has_permission:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail=f"Недостаточно прав: требуется {permission_code.value}",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
