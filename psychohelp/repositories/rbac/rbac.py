"""
Репозиторий для работы с RBAC (ролями и правами доступа)
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from psychohelp.config.database import get_async_db
from psychohelp.models import User, Role, Permission
from psychohelp.repositories.rbac import exceptions as exc
from psychohelp.constants.rbac import RoleCode, PermissionCode


async def get_user_roles(user_id: UUID) -> list[Role]:
    async with get_async_db() as session:
        result = await session.execute(
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            return []
        
        return list(user.roles)


async def get_user_permissions(user_id: UUID) -> list[str]:
    async with get_async_db() as session:
        result = await session.execute(
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions)
            )
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            return []
        
        permissions = set()
        for role in user.roles:
            for permission in role.permissions:
                permissions.add(permission.code.value)
        
        return list(permissions)


async def get_role_by_code(role_code: str | RoleCode) -> Role | None:
    async with get_async_db() as session:
        if isinstance(role_code, str):
            try:
                role_code = RoleCode[role_code] if role_code.isupper() else RoleCode(role_code)
            except (ValueError, KeyError):
                return None
        
        result = await session.execute(
            select(Role).where(Role.code == role_code)
        )
        return result.scalar_one_or_none()


async def get_all_roles() -> list[Role]:
    async with get_async_db() as session:
        result = await session.execute(select(Role))
        return list(result.scalars().all())


async def assign_role_to_user(user_id: UUID, role_code: str) -> bool:
    async with get_async_db() as session:
        async with session.begin():
            user_result = await session.execute(
                select(User)
                .options(selectinload(User.roles))
                .where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if user is None:
                raise exc.UserNotFoundException(user_id)
            
            try:
                role_enum = RoleCode[role_code] if role_code.isupper() else RoleCode(role_code)
            except (ValueError, KeyError):
                raise exc.RoleNotFoundException(role_code)
            
            role_result = await session.execute(
                select(Role).where(Role.code == role_enum)
            )
            role = role_result.scalar_one_or_none()
            
            if role is None:
                raise exc.RoleNotFoundException(role_code)
            
            if role in user.roles:
                return False
            
            user.roles.append(role)
            await session.commit()
            
            return True


async def remove_role_from_user(user_id: UUID, role_code: str) -> bool:
    async with get_async_db() as session:
        async with session.begin():
            user_result = await session.execute(
                select(User)
                .options(selectinload(User.roles))
                .where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if user is None:
                raise exc.UserNotFoundException(user_id)
            
            role = next((r for r in user.roles if r.code.value == role_code), None)
            
            if role is None:
                return False
            
            user.roles.remove(role)
            await session.commit()
            
            return True


async def get_permission_by_code(permission_code: str | PermissionCode) -> Permission | None:
    async with get_async_db() as session:
        if isinstance(permission_code, str):
            try:
                permission_code = PermissionCode[permission_code] if permission_code.isupper() else PermissionCode(permission_code)
            except (ValueError, KeyError):
                return None
        
        result = await session.execute(
            select(Permission).where(Permission.code == permission_code)
        )
        return result.scalar_one_or_none()


async def get_all_permissions() -> list[Permission]:
    async with get_async_db() as session:
        result = await session.execute(select(Permission))
        return list(result.scalars().all())


async def get_permissions_by_resource(resource: str) -> list[Permission]:
    async with get_async_db() as session:
        result = await session.execute(
            select(Permission).where(Permission.resource == resource)
        )
        return list(result.scalars().all())


