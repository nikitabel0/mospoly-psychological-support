import httpx
import os


def client():
    """
    Создать HTTP клиент для тестов.
    
    Настройки можно переопределить через переменные окружения:
    - TEST_API_HOST: хост сервера (по умолчанию: localhost)
    - TEST_API_PORT: порт сервера (по умолчанию: 8000)
    - TEST_API_TIMEOUT: таймаут запросов в секундах (по умолчанию: 30)
    
    Пример:
        export TEST_API_HOST=0.0.0.0
        export TEST_API_PORT=8080
        pytest tests/
    """
    host = os.getenv("TEST_API_HOST", "localhost")
    port = os.getenv("TEST_API_PORT", "8000")
    timeout = float(os.getenv("TEST_API_TIMEOUT", "30.0"))
    
    base_url = f"http://{host}:{port}"
    
    return httpx.AsyncClient(
        base_url=base_url,
        follow_redirects=True,
        timeout=timeout
    )
