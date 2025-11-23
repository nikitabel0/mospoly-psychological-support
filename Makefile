-include .env
export

up:
	docker compose -f docker-compose.yml up -d

down:
	docker compose -f docker-compose.yml down

# Development commands
install:
	uv sync --dev

lint:
	uv run ruff check .

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

test:
	uv run pytest tests/ -v

test-cov:
	uv run pytest tests/ --cov=psychohelp --cov-report=html --cov-report=term

# Combined commands
check: lint format-check test

fix: format
	uv run ruff check --fix .

# Применить миграции
migrate:
	docker compose exec app bash -c "POSTGRES_HOST=db uv run alembic upgrade head"

# Создать новую миграцию (использование: make migrate-create MESSAGE="описание")
migrate-create:
	docker compose exec app bash -c "POSTGRES_HOST=db uv run alembic revision --autogenerate -m '$(MESSAGE)'"

# Откатить последнюю миграцию
migrate-rollback:
	docker compose exec app bash -c "POSTGRES_HOST=db uv run alembic downgrade -1"

# Показать текущую версию миграции
migrate-status:
	docker compose exec app bash -c "POSTGRES_HOST=db uv run alembic current"

# Показать историю миграций
migrate-history:
	docker compose exec app bash -c "POSTGRES_HOST=db uv run alembic history"

.PHONY: up down install lint format format-check test test-cov check fix migrate migrate-create migrate-rollback migrate-status migrate-history
