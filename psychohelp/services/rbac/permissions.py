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
    """
    Получить все права (permission codes) пользователя через его роли
    
    Args:
        user_id: ID пользователя
        
    Returns:
        list[str]: Список кодов прав доступа
    """
    return await repo_get_user_permissions(user_id)


async def user_has_permission(user_id: UUID, permission_code: PermissionCode) -> bool:
    """
    Проверить, есть ли у пользователя конкретное право
    
    Args:
        user_id: ID пользователя
        permission_code: Код права
        
    Returns:
        bool: True если право есть, False если нет
    """
    permissions = await get_user_permissions(user_id)
    return permission_code.value in permissions


async def user_has_any_permission(user_id: UUID, permission_codes: list[PermissionCode]) -> bool:
    """
    Проверить, есть ли у пользователя хотя бы одно из указанных прав
    
    Args:
        user_id: ID пользователя
        permission_codes: Список кодов прав
        
    Returns:
        bool: True если есть хотя бы одно право
    """
    permissions = await get_user_permissions(user_id)
    return any(code.value in permissions for code in permission_codes)


def require_permission(permission_code: PermissionCode):
    """
    Декоратор для проверки наличия права у пользователя
    
    Args:
        permission_code: Код требуемого права
        
    Usage:
        @router.get("/protected")
        @require_permission(PermissionCode.APPOINTMENTS_VIEW_ALL)
        async def protected_endpoint(request: Request):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = None
            
            if 'request' in kwargs:
                request = kwargs['request']
            else:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if request is None:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Request object not found"
                )
            
            token = request.cookies.get("access_token")
            if not token:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Не авторизован"
                )
            
            # Получаем user_id из токена
            try:
                user_id = get_user_id_from_token(token)
            except Exception as e:
                # Любая ошибка при декодировании токена = невалидный токен
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Невалидный токен"
                ) from None
            
            # Проверяем право
            has_permission = await user_has_permission(user_id, permission_code)
            if not has_permission:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail=f"Недостаточно прав: требуется {permission_code.value}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

