# Development Guide

## Настройка воркфлоу с линтерами, форматтерами и тестами

Этот проект настроен с использованием Ruff для линтинга и форматирования кода, а также pytest для тестирования.

### Установка зависимостей

#### Windows
```bash
# Установка зависимостей
.\run.bat install

# Или вручную
python -m pip install -e .
python -m pip install ruff pytest pytest-asyncio
```

#### Linux/macOS
```bash
# Установка зависимостей
make install

# Или вручную
uv sync --dev
```

### Команды для разработки

#### Windows (run.bat)
```bash
# Проверка линтинга
.\run.bat lint

# Форматирование кода
.\run.bat format

# Проверка форматирования
.\run.bat format-check

# Запуск тестов
.\run.bat test

# Полная проверка (линт + формат + тесты)
.\run.bat check

# Автоматическое исправление проблем
.\run.bat fix
```

#### Linux/macOS (Makefile)
```bash
# Проверка линтинга
make lint

# Форматирование кода
make format

# Проверка форматирования
make format-check

# Запуск тестов
make test

# Тесты с покрытием
make test-cov

# Полная проверка (линт + формат + тесты)
make check

# Автоматическое исправление проблем
make fix
```

### GitHub Actions

При каждом push или создании pull request автоматически запускается:

1. **Линтинг** - проверка кода с помощью Ruff
2. **Форматирование** - проверка форматирования кода
3. **Тесты** - запуск тестов с PostgreSQL

### Конфигурация Ruff

Настройки Ruff находятся в `pyproject.toml`:

```toml
[tool.ruff]
target-version = "py38"
line-length = 88

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
ignore = [
    "E501",  # line too long, handled by black
    "B008",  # do not perform function calls in argument defaults
    "C901",  # too complex
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]

[tool.ruff.lint.isort]
known-first-party = ["psychohelp"]
```

### Рекомендации

1. **Перед коммитом** всегда запускайте `.\run.bat check` (Windows) или `make check` (Linux/macOS)
2. **Автоматическое исправление** - используйте `.\run.bat fix` или `make fix` для исправления большинства проблем
3. **Форматирование** - код автоматически форматируется при сохранении (если настроен в IDE)
4. **Тесты** - пишите тесты для новой функциональности

### Структура проекта

```
├── .github/workflows/    # GitHub Actions воркфлоу
├── psychohelp/          # Основной код приложения
├── tests/               # Тесты
├── Makefile            # Команды для Linux/macOS
├── run.bat             # Команды для Windows
├── pyproject.toml      # Конфигурация проекта и Ruff
└── README.md           # Документация проекта
```
