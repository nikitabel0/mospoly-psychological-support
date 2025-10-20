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

.PHONY: up down install lint format format-check test test-cov check fix
