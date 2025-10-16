# Психологическая Служба Московского политехнического университета

Веб-сервис для организации психологической поддержки студентов Московского политехнического университета.

## Структура каталогов

```
mospoly-psychological-support/
├── psychohelp/                  # Основной пакет приложения
│   ├── config/                  # Конфигурация базы данных
│   │   ├── __init__.py
│   │   └── database.py
│   ├── models/                  # SQLAlchemy модели
│   │   ├── appointments.py      # Модель записей на консультации
│   │   ├── reviews.py           # Модель отзывов
│   │   ├── roles.py             # Модель ролей пользователей
│   │   ├── therapists.py        # Модель психологов
│   │   └── users.py             # Модель пользователей
│   ├── repositories/            # Слой доступа к данным
│   │   ├── appointments.py
│   │   ├── reviews.py
│   │   ├── roles.py
│   │   ├── therapists.py
│   │   └── users.py
│   ├── routes/                   # API маршруты
│   │   └── controllers/          # Контроллеры для обработки запросов
│   │       ├── appointments.py
│   │       ├── images.py
│   │       ├── reviews.py
│   │       ├── roles.py
│   │       ├── therapists.py
│   │       └── users.py
│   ├── schemas/                  # Pydantic схемы для валидации
│   │   ├── appointments.py
│   │   ├── reviews.py
│   │   ├── therapists.py
│   │   └── users.py
│   ├── services/                 # Бизнес-логика
│   │   ├── appointments.py
│   │   ├── reviews.py
│   │   ├── roles.py
│   │   ├── therapists.py
│   │   └── users.py
│   └── main.py                   # Точка входа приложения
├── tests/                        # Тесты
│   ├── conftest.py
│   └── test_users.py
├── docker-compose.yml            # Docker Compose конфигурация
├── Dockerfile                    # Docker образ
├── pyproject.toml                # Конфигурация проекта и зависимости
├── swagger.yaml                  # OpenAPI спецификация
└── uv.lock                       # Файл блокировки зависимостей
```

## Используемый стек

### Backend
- **FastAPI** - современный веб-фреймворк для создания API
- **SQLAlchemy** - ORM для работы с базой данных
- **PostgreSQL** - реляционная база данных
- **AsyncPG** - асинхронный драйвер PostgreSQL
- **Pydantic** - валидация данных и сериализация
- **JWT** - аутентификация через токены
- **Passlib** - хеширование паролей

### Инфраструктура
- **Docker** - контейнеризация приложения
- **Docker Compose** - оркестрация сервисов
- **UV** - быстрый менеджер пакетов Python
- **Uvicorn** - ASGI сервер для FastAPI

### Разработка
- **Pytest** - фреймворк для тестирования
- **Pytest-asyncio** - поддержка асинхронного тестирования

## Установка и запуск

### Предварительные требования

- Python 3.13
- Docker и Docker Compose
- UV

### Локальная разработка

1. **Клонирование репозитория:**
   ```
   git clone https://github.com/nikitabel0/mospoly-psychological-support.git
   cd mospoly-psychological-support
   ```

2. **Установка зависимостей:**
   ```
   uv pip install -e .
   ```

3. **Запуск базы данных:**
   ```
   docker-compose up db -d
   ```

4. **Запуск приложения:**
   ```
   uv run python -m psychohelp.main
   ```

### Docker (рекомендуется)

1. **Запуск всех сервисов:**
   ```
   docker-compose up --build
   ```

2. **Запуск в фоновом режиме:**
   ```
   docker-compose up -d --build
   ```

3. **Остановка сервисов:**
   ```
   docker-compose down
   ```

## Базовые команды

### Разработка

```
# Установка зависимостей для разработки
uv pip install -e ".[dev]"

# Запуск тестов
pytest

# Запуск тестов с покрытием
pytest --cov=psychohelp

# Запуск линтера (если настроен)
flake8 psychohelp/
```

### Docker

```bash
# Пересборка и запуск
docker-compose up --build

# Просмотр логов
docker-compose logs -f app

# Выполнение команд в контейнере
docker-compose exec app bash

# Очистка volumes
docker-compose down -v
```

### База данных

```bash
# Подключение к базе данных
docker-compose exec db psql -U postgres -d psychohelp

# Создание резервной копии
docker-compose exec db pg_dump -U postgres psychohelp > backup.sql

# Восстановление из резервной копии
docker-compose exec -T db psql -U postgres psychohelp < backup.sql
```
