from psychohelp.repositories import create_access_token, verify_password, hash_password
from psychohelp.repositories.users import (
    get_user_by_id as repo_get_user_by_id,
    get_user_by_email as repo_get_user_by_email,
    get_user_by_token as repo_get_user_by_token,
    create_user,
    UUID,
)
from psychohelp.models.users import User
from psychohelp.services.users import exceptions, models


async def get_user_by_id(user_id: UUID) -> User | None:
    return await repo_get_user_by_id(user_id)


async def get_user_by_email(email: str) -> User | None:
    return await repo_get_user_by_email(email)


async def get_user_by_token(token: str) -> User | None:
    return await repo_get_user_by_token(token)


async def register_user(
    first_name: str,
    last_name: str,
    phone_number: str,
    email: str,
    password: str,
    middle_name: str | None = None,
    social_media: str | None = None,
) -> tuple[User, str]:
    new_user = await create_user(
        first_name,
        last_name,
        phone_number,
        email,
        hash_password(password),
        middle_name,
        social_media,
    )
    return new_user, create_access_token(new_user.id)


async def login_user(email: str, password: str) -> models.UserWithToken:
    user = await repo_get_user_by_email(email)
    if user is None:
        raise exceptions.UserNotFound()

    if not verify_password(password, user.password):
        raise exceptions.WrongPassword()

    return models.UserWithToken(
        user=user,
        token=create_access_token(user.id),
    )
