import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "DEBUG",
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None,
) -> None:
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    handlers: list[logging.Handler] = [
        logging.StreamHandler(sys.stdout)
    ]

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(
            logging.FileHandler(log_file, encoding="utf-8")
        )

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=handlers,
        force=True,
    )

    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

