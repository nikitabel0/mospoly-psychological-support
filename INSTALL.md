# Инструкция по развёртыванию на сервере БЕЗ Docker

## ✅ Компилировать ничего не нужно! Это Python проект.

---

## Шаг 1: Установите зависимости на сервере

Выполните на сервере:

```bash
# 1. Установите Python и системные зависимости
sudo apt update
sudo apt install python3.13 python3-pip python3-venv postgresql postgresql-contrib

# 2. Установите UV (менеджер пакетов Python)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # или перезайдите в терминал
```

---

## Шаг 2: Настройте PostgreSQL

```bash
# 1. Подключитесь к PostgreSQL
sudo -u postgres psql

# 2. В консоли PostgreSQL выполните:
CREATE USER myuser WITH PASSWORD 'your_secure_password';
CREATE DATABASE mydatabase;
GRANT ALL PRIVILEGES ON DATABASE mydatabase TO myuser;
\q  # выйти
```

**ВАЖНО:** Замените `'your_secure_password'` на надёжный пароль!

---

## Шаг 3: Скопируйте проект на сервер

```bash
# С вашего компьютера
scp -r mospoly-psychological-support-main user@your-server-ip:/path/to/destination/

# Или клонируйте через git на сервере
git clone <your-repo-url>
```

---

## Шаг 4: Создайте файл с настройками

На сервере в корне проекта создайте файл `.env`:

```bash
cd /path/to/mospoly-psychological-support-main
nano .env
```

Содержимое `.env`:
```bash
POSTGRES_USER=myuser
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=mydatabase
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
APP_PORT=8000
RESET_DB_ON_START=false
LOG_LEVEL=INFO
```

---

## Шаг 5: Установите зависимости Python

```bash
# В корне проекта
cd /path/to/mospoly-psychological-support-main

# Установите зависимости
uv pip install -e .
```

---

## Шаг 6: Настройте миграции базы данных

```bash
# Установите переменные окружения
export POSTGRES_USER=myuser
export POSTGRES_PASSWORD=your_secure_password
export POSTGRES_DB=mydatabase
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432

# Примените миграции
uv run alembic upgrade head
```

---

## Шаг 7: Запустите приложение

### Вариант A: Простой запуск (для теста)

```bash
uv run python -m psychohelp.main
```

Приложение будет доступно на `http://your-server-ip:8000`

### Вариант B: Запуск в фоне с логированием

```bash
nohup uv run python -m psychohelp.main > app.log 2>&1 &
```

### Вариант C: Через screen (можно отключиться)

```bash
# Создайте сессию screen
screen -S psychohelp

# Запустите приложение
uv run python -m psychohelp.main

# Отключитесь: нажмите Ctrl+A, затем D
# Подключиться обратно: screen -r psychohelp
```

---

## ✅ Проверка работы

1. Проверьте, что приложение запущено:
```bash
curl http://localhost:8000/docs
```

2. Откройте в браузере: `http://your-server-ip:8000/docs`

---

## Автозапуск при перезагрузке сервера (опционально)

Создайте systemd service:

```bash
sudo nano /etc/systemd/system/psychohelp.service
```

Содержимое файла:
```ini
[Unit]
Description=Psychological Help API Service
After=network.target postgresql.service

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/mospoly-psychological-support-main
Environment="POSTGRES_USER=myuser"
Environment="POSTGRES_PASSWORD=your_secure_password"
Environment="POSTGRES_DB=mydatabase"
Environment="POSTGRES_HOST=localhost"
Environment="POSTGRES_PORT=5432"
Environment="LOG_LEVEL=INFO"
ExecStart=/home/your-username/.local/bin/uv run python -m psychohelp.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активируйте сервис:
```bash
sudo systemctl daemon-reload
sudo systemctl enable psychohelp
sudo systemctl start psychohelp

# Проверьте статус
sudo systemctl status psychohelp

# Просмотр логов
journalctl -u psychohelp -f
```

---

## Управление приложением

```bash
# Остановить
pkill -f "psychohelp.main"

# Или если через systemd
sudo systemctl stop psychohelp

# Запустить
sudo systemctl start psychohelp

# Перезапустить
sudo systemctl restart psychohelp
```

---

## Важно для продакшена

В файле `psychohelp/main.py` на строке 88 замените:
```python
reload=True,  # ❌ НЕ используйте reload=True на сервере
```

На:
```python
reload=False,  # ✅ Для продакшена всегда False
```

Это повысит производительность и безопасность.






