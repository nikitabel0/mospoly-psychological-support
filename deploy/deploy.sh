#!/usr/bin/env bash
# Разворачивает бэкенд на стенде. Запускается из CI по SSH после git reset,
# либо руками на сервере. Стенд определяется переменной STAND в .env.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

# Деплои обоих репозиториев идут на один сервер. Одновременная сборка фронта
# и бэкенда не влезает в память, а два "docker image prune" начинают гонку.
# Замок выстраивает деплои в очередь независимо от того, кто их запустил.
exec 9>/tmp/psycho-deploy.lock
flock -w 900 9 || {
    echo "Другой деплой идёт дольше 15 минут, выхожу" >&2
    exit 1
}

COMPOSE=(docker compose -f docker-compose.stand.yml)

if [[ ! -f .env ]]; then
    echo "Нет .env рядом с docker-compose.stand.yml - скопируйте .env.stand.example и заполните" >&2
    exit 1
fi

echo "==> Сборка образа"
"${COMPOSE[@]}" build

echo "==> Миграции"
# Одноразовый контейнер. depends_on поднимет db и дождётся её healthcheck,
# поэтому --no-deps здесь ставить нельзя - alembic упрётся в недоступную базу.
"${COMPOSE[@]}" run --rm api alembic upgrade head || {
    echo "Миграции не применились, деплой остановлен" >&2
    exit 1
}

echo "==> Запуск"
"${COMPOSE[@]}" up -d --remove-orphans

echo "==> Очистка старых образов"
docker image prune -f >/dev/null

echo "==> Готово"
"${COMPOSE[@]}" ps
