from uuid import UUID

from sqlalchemy import delete, select

from psychohelp.config.database import get_async_db
from psychohelp.models.roles import Role, UserRole


async def get_roles_by_user_id(user_id: UUID):
    async with get_async_db() as session:
        result = await session.execute(select(Role).filter(Role.user_id == user_id))
    return result.scalars().all()


async def add_roles_by_user_id(user_id: UUID, roles: list[UserRole]):
    new_roles = [Role(user_id=user_id, role=role) for role in roles]
    async with get_async_db() as session:
        for role in new_roles:
            await session.merge(role)
        await session.commit()


async def delete_roles_by_user_id(user_id: UUID, roles: list[UserRole]):
    async with get_async_db() as session:
        await session.execute(delete(Role).filter(Role.role.in_(roles)))
        await session.commit()
