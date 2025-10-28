import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine

from psychohelp.config.database import (
    Base,
    config,
)
from psychohelp.config.logging import setup_logging, get_logger
from psychohelp.routes import api_router

from psychohelp.models import users, therapists, appointments, reviews, roles

import uvicorn

log_level = os.getenv("LOG_LEVEL", "DEBUG")
log_file_path = os.getenv("LOG_FILE")

setup_logging(
    level=log_level,
    log_file=Path(log_file_path) if log_file_path else None,
)

logger = get_logger(__name__)


async def reset_database(engine: AsyncEngine) -> None:
    logger.warning("Resetting database - dropping all tables")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database reset completed")


engine = create_async_engine(config.DATABASE_URL, echo=False)


def get_application() -> FastAPI:
    application = FastAPI()
    application.include_router(api_router)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://psychohelp.example.com",
            "https://185.128.105.126",
            "http://localhost:3000",
            "http://localhost:8000",
            "http://localhost",
            "http://185.128.105.126:8000",
            "http://185.128.105.126:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.on_event("startup")
    async def on_startup() -> None:
        logger.info("Starting application")

        if config.RESET_DB_ON_START:
            await reset_database(engine)
        logger.info("Application started successfully")

    @application.on_event("shutdown")
    async def on_shutdown() -> None:
        logger.info("Shutting down application")

    return application


app = get_application()


def main() -> None:
    uvicorn.run(
        "psychohelp.main:app",
        host=config.APP_HOST,
        port=config.APP_PORT,
        reload=True,
        log_config=None,
        log_level=log_level.lower(),
    )


if __name__ == "__main__":
    main()
