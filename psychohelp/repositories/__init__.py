from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from passlib.context import CryptContext

from psychohelp.config import ACCESS_TOKEN_EXPIRE, ALGORITHM, SECRET_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(sub: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    now = datetime.now(UTC)
    encoded = jwt.encode(
        {"sub": str(sub), "exp": expire, "iat": now},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded


def get_user_id_from_token(token: str) -> UUID:
    decoded = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        options={"verify_iat": True, "verify_exp": True, "verify_signature": True},
    )

    return UUID(decoded["sub"])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)
