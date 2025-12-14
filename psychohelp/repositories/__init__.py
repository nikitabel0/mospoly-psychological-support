from psychohelp.config.database import config
from psychohelp.config import REFRESH_TOKEN_EXPIRE, SECRET_KEY, ALGORITHM
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

from uuid import UUID

import jwt


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(sub: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    now = datetime.now(timezone.utc)
    encoded = jwt.encode(
        {"sub": str(sub), "exp": expire, "iat": now},
        config.SECRET_KEY,
        algorithm=config.ALGORITHM,
    )
    return encoded

def create_refresh_token(sub: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE)
    now = datetime.now(timezone.utc)
    encoded = jwt.encode(
        {"sub": str(sub), "exp": expire, "iat": now},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded

def refresh_access_token(refresh_token: str) -> str:
    decoded = jwt.decode(
        refresh_token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
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
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)
