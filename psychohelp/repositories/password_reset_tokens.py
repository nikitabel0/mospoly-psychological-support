from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update

from psychohelp.config.config import get_async_db
from psychohelp.models.password_reset_tokens import PasswordResetToken
from psychohelp.models.users import User


async def create_password_reset_token(
    user_id: UUID,
    token_hash: str,
    expires_at: datetime,
    now: datetime,
) -> PasswordResetToken:
    async with get_async_db() as session:
        async with session.begin():
            await session.execute(
                update(PasswordResetToken)
                .where(
                    PasswordResetToken.user_id == user_id,
                    PasswordResetToken.used_at.is_(None),
                )
                .values(used_at=now)
            )

            reset_token = PasswordResetToken(
                user_id=user_id,
                token_hash=token_hash,
                expires_at=expires_at,
            )
            session.add(reset_token)
            await session.flush()
            return reset_token


async def invalidate_password_reset_token(token_hash: str, now: datetime) -> None:
    async with get_async_db() as session:
        async with session.begin():
            await session.execute(
                update(PasswordResetToken)
                .where(
                    PasswordResetToken.token_hash == token_hash,
                    PasswordResetToken.used_at.is_(None),
                )
                .values(used_at=now)
            )


async def use_password_reset_token(
    token_hash: str,
    hashed_password: str,
    now: datetime,
) -> bool:
    async with get_async_db() as session:
        async with session.begin():
            result = await session.execute(
                select(PasswordResetToken)
                .where(
                    PasswordResetToken.token_hash == token_hash,
                    PasswordResetToken.used_at.is_(None),
                    PasswordResetToken.expires_at > now,
                )
                .with_for_update()
            )
            reset_token = result.scalar_one_or_none()
            if reset_token is None:
                return False

            await session.execute(
                update(User)
                .where(User.id == reset_token.user_id)
                .values(password=hashed_password)
            )
            reset_token.used_at = now
            return True
