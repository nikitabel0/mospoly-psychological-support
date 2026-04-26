from uuid import UUID
from sqlalchemy import select, update, and_, or_
from sqlalchemy.exc import IntegrityError
from psychohelp.config.config import get_async_db
from psychohelp.models.applications import Application, ApplicationStatus
from sqlalchemy.orm import selectinload


async def create_application(application_data: dict) -> Application:
    async with get_async_db() as session:
        application = Application(**application_data)
        session.add(application)
        await session.commit()
        # Для свежесозданной заявки нам тоже нужно загрузить реляции, чтобы Pydantic не ругался
        # Используем подгрузку после создания
        stmt = select(Application).options(
            selectinload(Application.user)
        ).where(Application.id == application.id)
        
        result = await session.execute(stmt)
        return result.scalar_one()


async def get_application_by_id(application_id: UUID) -> Application | None:
    async with get_async_db() as session:
        result = await session.execute(
            select(Application)
            .options( # <--- ДОБАВЛЯЕМ ОПЦИИ ЗАГРУЗКИ СВЯЗЕЙ
                selectinload(Application.user),
                selectinload(Application.assigned_to_user),
                selectinload(Application.psychologist),
                selectinload(Application.appointment)
            )
            .where(Application.id == application_id)
        )
        return result.scalar_one_or_none()


async def get_applications(
    skip: int = 0,
    limit: int = 100,
    status: ApplicationStatus | None = None,
    assigned_to: UUID | None = None,
    user_id: UUID | None = None,
    sort_by: str = "created_at",
    sort_desc: bool = True,
) -> list[Application]:
    async with get_async_db() as session:
        query = select(Application).options( # <--- ДОБАВЛЯЕМ ТУТ ТОЖЕ
            selectinload(Application.user),
            selectinload(Application.assigned_to_user),
            selectinload(Application.psychologist),
            selectinload(Application.appointment)
        )
        
        filters = []
        if status:
            filters.append(Application.status == status.value)
        if assigned_to:
            filters.append(Application.assigned_to == assigned_to)
        if user_id:
            filters.append(Application.user_id == user_id)
        if filters:
            query = query.where(and_(*filters))
        if sort_by:
            order = getattr(Application, sort_by).desc() if sort_desc else getattr(Application, sort_by).asc()
            query = query.order_by(order)
            
        query = query.offset(skip).limit(limit)
        result = await session.execute(query)
        return list(result.scalars().all())


async def update_application_with_version(
    application_id: UUID,
    expected_version: int,
    update_data: dict
) -> Application | None:
    """Обновление с оптимистичной блокировкой. Возвращает None при конфликте версий."""
    async with get_async_db() as session:
        stmt = (
            update(Application)
            .where(Application.id == application_id, Application.version == expected_version)
            .values(**update_data, version=Application.version + 1)
            .returning(Application)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.scalar_one_or_none()


async def update_application(application_id: UUID, update_data: dict) -> Application | None:
    """Простое обновление без проверки версии (использовать с осторожностью)."""
    async with get_async_db() as session:
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
    async with get_async_db() as session:
        application = await session.get(Application, application_id)
        if application:
            await session.delete(application)
            await session.commit()
            return True
        return False