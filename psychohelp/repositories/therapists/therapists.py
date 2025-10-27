from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from psychohelp.config.database import get_async_db
from psychohelp.models.therapists import Therapist
from psychohelp.models.users import User
from psychohelp.models.roles import Role
from psychohelp.repositories.therapists import exceptions as exc


async def get_therapist_by_id(therapist_id: UUID):
    async with get_async_db() as session:
        result = await session.execute(
            select(Therapist)
            .options(selectinload(Therapist.user))
            .filter(Therapist.id == therapist_id)
        )
        therapist = result.scalar_one_or_none()

    return therapist


async def get_therapists(skip: int = 0, take: int = 10):
    """
    Получить список психологов с пагинацией
    """
    async with get_async_db() as session:
        query = await session.execute(
            select(Therapist)
            .options(joinedload(Therapist.user))
            .offset(skip)
            .limit(take)
        )

    result = query.scalars().all()
    return result


async def create_therapist(user_id: UUID, therapist_data: dict) -> Therapist:
    async with get_async_db() as session:
        async with session.begin():
            user_result = await session.execute(
                select(User)
                .options(selectinload(User.roles))
                .where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if user is None:
                raise exc.UserNotFoundForTherapistException(user_id)
            
            existing_therapist_result = await session.execute(
                select(Therapist).where(Therapist.user_id == user_id)
            )
            if existing_therapist_result.scalar_one_or_none() is not None:
                raise exc.TherapistAlreadyExistsException(user_id)
            
            therapist = Therapist(user_id=user_id, **therapist_data)
            session.add(therapist)
            
            psychologist_role_result = await session.execute(
                select(Role).where(Role.code == "psychologist")
            )
            psychologist_role = psychologist_role_result.scalar_one_or_none()
            
            if not psychologist_role:
                raise exc.PsychologistRoleNotFoundException()
            
            user_role_codes = {role.code for role in user.roles}
            
            if "psychologist" not in user_role_codes:
                user.roles.append(psychologist_role)
            
            await session.flush()
            await session.refresh(therapist)
            await session.commit()
    
    return therapist


async def delete_therapist(therapist_id: UUID) -> bool:
    """
    Удалить запись терапевта и убрать роль 'psychologist' у пользователя
    
    Args:
        therapist_id: UUID терапевта
        
    Returns:
        bool: True если удалено, False если не найдено
    """
    async with get_async_db() as session:
        async with session.begin():
            result = await session.execute(
                select(Therapist)
                .options(selectinload(Therapist.user).selectinload(User.roles))
                .where(Therapist.id == therapist_id)
            )
            therapist = result.scalar_one_or_none()
            
            if therapist is None:
                return False
            
            user = therapist.user
            
            psychologist_role = next(
                (role for role in user.roles if role.code == "psychologist"),
                None
            )
            if psychologist_role:
                user.roles.remove(psychologist_role)
            
            await session.delete(therapist)
            await session.commit()
    
    return True

