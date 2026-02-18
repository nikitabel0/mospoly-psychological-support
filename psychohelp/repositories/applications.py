
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from psychohelp.config.config import async_session
from psychohelp.models.applications import Application, ApplicationStatus


async def create_application(application_data: dict) -> Application:
    async with async_session() as session:
        application = Application(**application_data)
        session.add(application)
        await session.commit()
        await session.refresh(application)
        return application


async def get_application_by_id(application_id: UUID) -> Application | None:
    async with async_session() as session:
        result = await session.execute(
            select(Application).where(Application.id == application_id)
        )
        return result.scalar_one_or_none()


async def get_applications(
    skip: int = 0,
    limit: int = 100,
    status: ApplicationStatus | None = None
) -> list[Application]:
    async with async_session() as session:
        query = select(Application)
        if status:
            query = query.where(Application.status == status)
        query = query.offset(skip).limit(limit)
        result = await session.execute(query)
        return list(result.scalars().all())


async def update_application(application_id: UUID, update_data: dict) -> Application | None:
    async with async_session() as session:
        stmt = (
            update(Application)
            .where(Application.id == application_id)
            .values(**update_data)
            .returning(Application)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.scalar_one_or_none()


async def delete_application(application_id: UUID) -> bool:
    async with async_session() as session:
        application = await session.get(Application, application_id)
        if application:
            await session.delete(application)
            await session.commit()
            return True
        return False