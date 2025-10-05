from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from contextlib import asynccontextmanager


class Config:
    DATABASE_URL = ""


class LocalDevConfig(Config):
    DATABASE_URL = "postgresql+asyncpg://myuser:mypassword@localhost:5432/mydatabase"


class DevConfig(Config):
    DATABASE_URL = "postgresql+asyncpg://a_admin:superStrongPassword@185.128.105.126:5432/psychological"


configurations = {
    "local-dev": LocalDevConfig,
    "dev": DevConfig,
}

profile = "dev"
config = configurations[profile]

RESET_DB_ON_START = False
RESET_COOKIE_ON_START = True


@asynccontextmanager
async def get_async_db():
    from sqlalchemy import exc

    session: AsyncSession = async_session()
    try:
        yield session
    except exc.SQLAlchemyError:
        await session.rollback()
        raise
    finally:
        await session.close()


async_engine = create_async_engine(config.DATABASE_URL, future=True, echo=True)
async_session = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()
