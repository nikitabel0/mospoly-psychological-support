from datetime import datetime, timedelta, timezone
from hashlib import sha256
from html import escape
from secrets import token_urlsafe

from psychohelp.config.config import config
from psychohelp.config.logging import get_logger
from psychohelp.repositories import hash_password
from psychohelp.repositories import password_reset_tokens as reset_tokens_repo
from psychohelp.repositories.users import get_user_by_email
from psychohelp.services.email import EmailDeliveryError, EmailPayload, get_email_provider


logger = get_logger(__name__)


class InvalidPasswordResetToken(Exception):
    pass


PASSWORD_RESET_REQUEST_MESSAGE = (
    "Если пользователь с таким email существует, письмо для восстановления пароля будет отправлено"
)


def _hash_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def _build_reset_url(token: str) -> str:
    return config.PASSWORD_RESET_URL_TEMPLATE.format(token=token)


def _build_password_reset_email(reset_url: str) -> tuple[str, str, str]:
    subject = "Восстановление пароля"
    text = (
        "Вы запросили восстановление пароля.\n\n"
        f"Перейдите по ссылке, чтобы задать новый пароль: {reset_url}\n\n"
        "Если вы не запрашивали восстановление пароля, просто проигнорируйте это письмо."
    )
    html_url = escape(reset_url, quote=True)
    html = (
        "<p>Вы запросили восстановление пароля.</p>"
        f'<p><a href="{html_url}">Задать новый пароль</a></p>'
        "<p>Если вы не запрашивали восстановление пароля, просто проигнорируйте это письмо.</p>"
    )
    return subject, text, html


async def request_password_reset(email: str) -> str:
    user = await get_user_by_email(email)
    if user is None:
        return PASSWORD_RESET_REQUEST_MESSAGE

    token = token_urlsafe(32)
    token_hash = _hash_token(token)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=config.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)

    await reset_tokens_repo.create_password_reset_token(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
        now=now,
    )

    reset_url = _build_reset_url(token)
    subject, text, html = _build_password_reset_email(reset_url)

    try:
        await get_email_provider().send(
            EmailPayload(
                to=user.email,
                subject=subject,
                text=text,
                html=html,
                sender_alias=config.MAIL_FROM_NAME,
            )
        )
    except EmailDeliveryError:
        await reset_tokens_repo.invalidate_password_reset_token(token_hash, now)
        logger.exception(f"Failed to send password reset email to user {user.id}")
        raise

    return PASSWORD_RESET_REQUEST_MESSAGE


async def reset_password(token: str, new_password: str) -> None:
    now = datetime.now(timezone.utc)
    token_hash = _hash_token(token)
    updated = await reset_tokens_repo.use_password_reset_token(
        token_hash=token_hash,
        hashed_password=hash_password(new_password),
        now=now,
    )
    if not updated:
        raise InvalidPasswordResetToken()
