from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from psychohelp.config.database import get_async_db
from psychohelp.constants.rbac import RoleCode
from psychohelp.models.roles import Role
from psychohelp.models.users import User
from psychohelp.repositories.rbac.exceptions import (
    RoleNotFoundException,
    UserNotFoundException,
)


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


async def assign_role_to_user(user_id: UUID, role_code: RoleCode) -> bool:
    async with get_async_db() as session:
        async with session.begin():
            user_result = await session.execute(
                select(User)
                .options(selectinload(User.roles))
                .where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()

            if user is None:
                raise UserNotFoundException(user_id)

            role_result = await session.execute(
                select(Role).where(Role.code == role_code)
            )
            role = role_result.scalar_one_or_none()

            if role is None:
                raise RoleNotFoundException(role_code)

            if role in user.roles:
                return False

            user.roles.append(role)
            await session.commit()

            return True


async def remove_role_from_user(user_id: UUID, role_code: RoleCode) -> bool:
    async with get_async_db() as session:
        async with session.begin():
            user_result = await session.execute(
                select(User)
                .options(selectinload(User.roles))
                .where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()

            if user is None:
                raise UserNotFoundException(user_id)

            role = next((r for r in user.roles if r.code == role_code), None)

            if role is None:
                return False

            user.roles.remove(role)
            await session.commit()

            return True


