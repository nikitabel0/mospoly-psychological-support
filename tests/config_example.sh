#!/bin/bash
# Пример настройки переменных окружения для тестов

# Хост API сервера
export TEST_API_HOST=localhost

# Порт API сервера
export TEST_API_PORT=8000

# Таймаут запросов в секундах
export TEST_API_TIMEOUT=30.0

# Теперь можно запустить тесты:
# source tests/config_example.sh
# pytest tests/

# Или в одну строку:
# TEST_API_HOST=localhost TEST_API_PORT=8000 pytest tests/

