-include .env
export

up:
	docker compose -f docker-compose.yml up -d

down:
	docker compose -f docker-compose.yml down

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

# Переменные для тестов (можно переопределить в .env)
TEST_API_HOST ?= localhost
TEST_API_PORT ?= 8000
TEST_API_TIMEOUT ?= 30.0

test:
	docker-compose exec app bash -c "uv sync --extra dev && POSTGRES_HOST=db TEST_API_HOST=$(TEST_API_HOST) TEST_API_PORT=$(TEST_API_PORT) TEST_API_TIMEOUT=$(TEST_API_TIMEOUT) uv run pytest tests/ -v"


.PHONY: up down migrate migrate-create migrate-rollback migrate-status migrate-history test test-local
