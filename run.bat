@echo off
if "%1"=="install" (
    python -m pip install -e .
    python -m pip install ruff pytest pytest-asyncio
    goto :eof
)
if "%1"=="lint" (
    ruff check .
    goto :eof
)
if "%1"=="format" (
    ruff format .
    goto :eof
)
if "%1"=="format-check" (
    ruff format --check .
    goto :eof
)
if "%1"=="test" (
    python -m pytest tests/ -v
    goto :eof
)
if "%1"=="check" (
    ruff check .
    ruff format --check .
    python -m pytest tests/ -v
    goto :eof
)
if "%1"=="fix" (
    ruff format .
    ruff check --fix .
    goto :eof
)
echo Usage: run.bat [install|lint|format|format-check|test|check|fix]
