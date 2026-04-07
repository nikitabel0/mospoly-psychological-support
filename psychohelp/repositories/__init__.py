from psychohelp.config.config import config
from datetime import datetime, timedelta, timezone

from uuid import UUID

import bcrypt
import jwt


def create_access_token(sub: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    encoded = jwt.encode(
        {"sub": str(sub), "exp": expire, "iat": now},
        config.SECRET_KEY,
        algorithm=config.ALGORITHM,
    )
    return encoded

def create_refresh_token(sub: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=config.REFRESH_TOKEN_EXPIRE)
    encoded = jwt.encode(
        {"sub": str(sub), "exp": expire, "iat": now},
        config.SECRET_KEY,
        algorithm=config.ALGORITHM,
    )
    return encoded

def refresh_access_token(refresh_token: str) -> str:
    decoded = jwt.decode(
        refresh_token,
        config.SECRET_KEY,
        algorithms=[config.ALGORITHM],
        options={"verify_iat": True, "verify_exp": True, "verify_signature": True},
    )
    sub = decoded["sub"]
    return create_access_token(sub)

def get_user_id_from_token(token: str) -> UUID:
    decoded = jwt.decode(
        token,
        config.SECRET_KEY,
        algorithms=[config.ALGORITHM],
        options={"verify_iat": True, "verify_exp": True, "verify_signature": True},
    )

    return UUID(decoded["sub"])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain = (plain_password or "").strip()
    h = (hashed_password or "").strip()
    if not plain or not h or not h.startswith(("$2a$", "$2b$", "$2y$")):
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), h.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=12),
    ).decode("utf-8")
