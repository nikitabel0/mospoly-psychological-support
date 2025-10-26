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

# Локальные миграции (если БД запущена локально)
migrate-local:
	POSTGRES_USER=postgres POSTGRES_PASSWORD=postgres POSTGRES_DB=postgres POSTGRES_HOST=localhost POSTGRES_PORT=5432 uv run alembic upgrade head

migrate-create-local:
	POSTGRES_USER=postgres POSTGRES_PASSWORD=postgres POSTGRES_DB=postgres POSTGRES_HOST=localhost POSTGRES_PORT=5432 uv run alembic revision --autogenerate -m "$(MESSAGE)"

migrate-rollback-local:
	POSTGRES_USER=postgres POSTGRES_PASSWORD=postgres POSTGRES_DB=postgres POSTGRES_HOST=localhost POSTGRES_PORT=5432 uv run alembic downgrade -1

migrate-status-local:
	POSTGRES_USER=postgres POSTGRES_PASSWORD=postgres POSTGRES_DB=postgres POSTGRES_HOST=localhost POSTGRES_PORT=5432 uv run alembic current

migrate-history-local:
	POSTGRES_USER=postgres POSTGRES_PASSWORD=postgres POSTGRES_DB=postgres POSTGRES_HOST=localhost POSTGRES_PORT=5432 uv run alembic history

.PHONY: up down migrate migrate-create migrate-rollback migrate-status migrate-history migrate-local migrate-create-local migrate-rollback-local migrate-status-local migrate-history-local
