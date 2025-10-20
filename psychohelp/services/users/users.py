from psychohelp.repositories import create_access_token, hash_password, verify_password
from psychohelp.repositories.users import (
    UUID,
    create_user,
)
from psychohelp.repositories.users import (
    get_user_by_email as repo_get_user_by_email,
)
from psychohelp.repositories.users import (
    get_user_by_id as repo_get_user_by_id,
)
from psychohelp.repositories.users import (
    get_user_by_token as repo_get_user_by_token,
)
from psychohelp.services.users import exceptions, models


async def get_user_by_id(user_id: UUID):
    return await repo_get_user_by_id(user_id)


async def get_user_by_email(email: str):
    return await repo_get_user_by_email(email)


async def get_user_by_token(token: str):
    return await repo_get_user_by_token(token)


async def register_user(
    first_name: str,
    last_name: str,
    phone_number: str,
    email: str,
    password: str,
    middle_name: str | None = None,
    social_media: str | None = None,
):
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


async def login_user(email: str, password: str):
    user = await repo_get_user_by_email(email)
    if user is None:
        raise exceptions.UserNotFound()

    if not verify_password(password, user.password):
        raise exceptions.WrongPassword()

    return models.UserWithToken(
        user=user,
        token=create_access_token(user.id),
    )
