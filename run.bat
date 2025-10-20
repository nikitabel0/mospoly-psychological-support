@echo off
if "%1"=="install" (
    uv sync --dev
    goto :eof
)
if "%1"=="lint" (
    uv run ruff check .
    goto :eof
)
if "%1"=="format" (
    uv run ruff format .
    goto :eof
)
if "%1"=="format-check" (
    uv run ruff format --check .
    goto :eof
)
if "%1"=="test" (
    uv run pytest tests/ -v
    goto :eof
)
if "%1"=="check" (
    uv run ruff check .
    uv run ruff format --check .
    uv run pytest tests/ -v
    goto :eof
)
if "%1"=="fix" (
    uv run ruff format .
    uv run ruff check --fix .
    goto :eof
)
echo Usage: run.bat [install|lint|format|format-check|test|check|fix]
