# Документация проекта "Психологическая служба МосПоли"

**Последнее обновление**: 27 октября 2025 г.

## Содержание

1. [Обзор проекта](#обзор-проекта-психологическая-служба-мосполи)
   - Описание
   - Цели и задачи
   - Целевая аудитория
   - Ключевые функции
   - Преимущества системы
   - Технологический стек
   - Быстрый старт

2. [Бизнес-логика системы](#бизнес-логика-системы)
   - Основные бизнес-процессы
   - Бизнес-правила и ограничения
   - Валидация данных
   - Транзакции и целостность данных
   - Безопасность
   - Реализованные возможности

3. [Компоненты системы](#компоненты-системы)
   - Main Application
   - Configuration (database, logging, __init__)
   - Models
   - Repositories
   - Services
   - Routes/Controllers
   - Schemas
   - Tests
   - Взаимодействие компонентов
   - Конфигурация и окружение
   - Зависимости

---

# Обзор проекта "Психологическая служба МосПоли"

## Описание

Проект представляет собой веб-приложение для автоматизации работы психологической службы МосПоли. Система позволяет студентам записываться на консультации к психологам университета, а психологам — эффективно управлять своим расписанием и взаимодействовать с клиентами.

## Цели и задачи

### Основные цели:
1. **Упрощение процесса записи** - студенты могут самостоятельно записаться на консультацию
2. **Централизация информации** - вся информация о психологах и записях в одном месте
3. **Автоматизация управления** - уменьшение административной нагрузки
4. **Повышение доступности** - возможность онлайн-консультаций

### Задачи системы:
- ✅ Регистрация и аутентификация пользователей
- ✅ Управление профилями психологов с детальной информацией
- ✅ Создание и отмена записей на консультации
- ✅ Поддержка онлайн и офлайн встреч
- ✅ Система уведомлений о предстоящих встречах
- ✅ Сбор и отображение отзывов о консультациях
- ✅ Разграничение прав доступа по ролям

## Целевая аудитория

### 1. Студенты
- Основные пользователи системы
- Записываются на консультации
- Просматривают информацию о психологах
- Оставляют отзывы после встреч

### 2. Психологи
- Просматривают свои записи
- Управляют расписанием
- Проводят консультации (онлайн и офлайн)

### 3. Администраторы
- Управляют пользователями
- Добавляют и редактируют информацию о психологах
- Модерируют контент

### 4. Персонал (Stuff)
- Вспомогательный персонал службы
- Помогают с организацией консультаций

## Ключевые функции

### Управление пользователями
- Регистрация с валидацией данных
- Вход через email и пароль
- JWT-аутентификация с HTTP-only cookies
- Профили пользователей с контактной информацией

### Система записей
- Создание записи на консультацию
- Выбор типа встречи (онлайн/офлайн)
- Указание причины обращения
- Напоминания о предстоящих встречах
- Отмена записей
- История встреч

### Профили психологов
- Подробная информация о специалистах
- Опыт работы и квалификация
- Области консультирования
- Образование
- Номер кабинета
- Фотография
- Краткое и полное описание

### Отзывы
- Отзывы привязаны к конкретной встрече
- Временная метка
- Текстовый контент

## Преимущества системы

1. **Доступность 24/7** - запись в любое время
2. **Прозрачность** - информация о психологах всегда доступна
3. **Удобство** - простой интерфейс и понятная навигация
4. **Безопасность** - защита персональных данных (JWT, bcrypt)
5. **Гибкость** - поддержка онлайн и офлайн форматов
6. **Аналитика** - возможность анализа загруженности службы
7. **Логирование** - полная трассировка всех операций
8. **Версионирование БД** - Alembic миграции для безопасных обновлений
9. **Контейнеризация** - легкое развертывание через Docker

## Технологический стек

### Backend
- **Python 3.8+** - Язык программирования
- **FastAPI 0.115.0** - Современный async веб-фреймворк
- **SQLAlchemy 2.0.35** - ORM для работы с БД
- **Pydantic 2+** - Валидация данных
- **Uvicorn** - ASGI сервер

### База данных
- **PostgreSQL 17** - Реляционная БД
- **asyncpg** - Асинхронный драйвер
- **Alembic** - Миграции схемы

### Безопасность
- **JWT (PyJWT)** - Токены аутентификации
- **bcrypt (Passlib)** - Хеширование паролей
- **HTTP-only cookies** - Защита от XSS

### Инфраструктура
- **Docker & Docker Compose** - Контейнеризация
- **Make** - Автоматизация
- **uv** - Быстрый менеджер пакетов Python

### Разработка
- **pytest** - Тестирование
- **logging** - Встроенная система логов

## Быстрый старт

### Запуск через Docker (рекомендуется)

```bash
# Клонировать репозиторий
git clone <repository-url>
cd mospoly-psychological-support

# Запустить сервисы
make up

# Приложение доступно на http://localhost:8000
```

### Запуск локально

```bash
# Установить зависимости (с uv)
uv sync

# Или с pip
pip install -e .

# Настроить переменные окружения
export POSTGRES_HOST=localhost
export SECRET_KEY=your-secret-key
# ... другие переменные

# Применить миграции
alembic upgrade head

# Запустить приложение
psychohelp

# Или напрямую
python -m psychohelp.main
```

### Полезные команды

```bash
# Остановить Docker сервисы
make down

# Создать миграцию
alembic revision --autogenerate -m "описание"

# Запустить тесты
pytest

# Проверить логи
docker compose logs -f app
```

# Бизнес-логика системы

## Основные бизнес-процессы

### 1. 🔐 Регистрация и аутентификация

#### Процесс регистрации

```
┌─────────────┐
│  Пользователь│
│  вводит     │
│  данные     │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────┐
│ Валидация данных (Pydantic)  │
│ - Email формат               │
│ - Телефон в формате E164     │
│ - Пароль минимум 8 символов  │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Проверка уникальности email  │
└──────┬───────────────────────┘
       │
       ├─── Email существует → Ошибка 422
       │
       ▼
┌──────────────────────────────┐
│ Хеширование пароля (bcrypt)  │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Создание записи в БД         │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Генерация JWT токена         │
│ - sub: user_id               │
│ - exp: текущее время + TTL   │
│ - iat: текущее время         │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Установка cookie с токеном   │
│ - HttpOnly                   │
│ - Secure (prod)              │
│ - SameSite=None              │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Возврат данных пользователя  │
│ (без пароля)                 │
└──────────────────────────────┘
```

**Код**: `psychohelp/services/users.py::register_user`

**Бизнес-правила**:
1. Email должен быть уникальным
2. Пароль хешируется и никогда не хранится в открытом виде
3. После регистрации пользователь автоматически аутентифицирован
4. По умолчанию пользователь не имеет ролей (если не указано иначе)

---

#### Процесс входа

```
┌─────────────┐
│ Пользователь│
│ вводит      │
│ email+pass  │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────┐
│ Поиск пользователя по email  │
└──────┬───────────────────────┘
       │
       ├─── Не найден → Ошибка 401
       │
       ▼
┌──────────────────────────────┐
│ Проверка пароля              │
│ bcrypt.verify(plain, hash)   │
└──────┬───────────────────────┘
       │
       ├─── Не совпадает → Ошибка 401
       │
       ▼
┌──────────────────────────────┐
│ Генерация JWT токена         │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Установка cookie             │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Возврат данных пользователя  │
└──────────────────────────────┘
```

**Код**: `psychohelp/services/users.py::login_user`

**Бизнес-правила**:
1. Неверные данные не раскрывают, что именно неверно (email или пароль)
2. Используется медленное хеширование bcrypt (защита от брутфорса)
3. Токен имеет ограниченное время жизни

---

### 2. 📅 Создание записи на консультацию

```
┌─────────────┐
│ Студент     │
│ выбирает    │
│ психолога   │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────┐
│ Заполнение формы записи:     │
│ - Тип (Online/Offline)       │
│ - Причина (опционально)      │
│ - Время напоминания          │
│ - Место встречи              │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Валидация данных             │
│ - patient_id существует      │
│ - therapist_id существует    │
│ - patient_id ≠ therapist_id  │
└──────┬───────────────────────┘
       │
       ├─── Ошибка → 400
       │
       ▼
┌──────────────────────────────┐
│ Создание записи:             │
│ - status = "Approved"        │
│ - last_change_time = now()   │
│ - venue = указанное или ""   │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Сохранение в БД              │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Возврат созданной записи     │
└──────────────────────────────┘
```

**Код**: `psychohelp/services/appointments.py::create_appointment`

**Бизнес-правила**:
1. **Пациент не может быть терапевтом** в одной записи
2. **Статус по умолчанию**: `Accepted` (принята психологом)
3. **Venue обязательно**: для Online - ссылка, для Offline - автоматически берется office психолога
4. **last_change_time**: автоматически устанавливается при создании
5. **Проверка роли**: Терапевт должен иметь роль `Therapist`
6. Причина обращения опциональна (конфиденциальность)

**Возможные статусы записи**:
- `Approved` - Одобрена (создана)
- `Accepted` - Принята (психолог подтвердил)
- `Cancelled` - Отменена
- `Done` - Завершена

---

### 3. ❌ Отмена записи

```
┌─────────────┐
│ Пользователь│
│ отменяет    │
│ запись      │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────┐
│ Поиск записи по ID           │
└──────┬───────────────────────┘
       │
       ├─── Не найдена → 404
       │
       ▼
┌──────────────────────────────┐
│ Проверка текущего статуса    │
└──────┬───────────────────────┘
       │
       ├─── Уже отменена/завершена → 400
       │
       ▼
┌──────────────────────────────┐
│ Обновление записи:           │
│ - status = "Cancelled"       │
│ - last_change_time = now()   │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Сохранение изменений         │
└──────────────────────────────┘
```

**Код**: `psychohelp/services/appointments.py::cancel_appointment_by_id`

**Бизнес-правила**:
1. Нельзя отменить уже отмененную запись
2. Нельзя отменить завершенную запись
3. При отмене обновляется last_change_time
4. История сохраняется (запись не удаляется)

---

### 4. 👨‍⚕️ Управление профилями психологов

#### Структура информации о психологе

Психолог - это расширенная информация о пользователе с ролью `Therapist`:

```
User (базовая информация)
├── ФИО
├── Контакты (email, телефон, соцсети)
└── Аутентификация

Therapist (профессиональная информация)
├── Опыт работы
├── Квалификация
├── Области консультирования
├── Образование
├── Описание
├── Краткое описание
├── Номер кабинета
└── Фотография
```

**Бизнес-правила**:
1. Профиль психолога создается отдельно от пользователя
2. ID психолога = ID пользователя (One-to-One)
3. Только пользователи с ролью `Therapist` могут иметь профиль
4. Фотография опциональна

---

### 5. 📝 Система отзывов

```
┌─────────────┐
│ Встреча     │
│ завершена   │
│ (Done)      │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────┐
│ Пациент может оставить отзыв │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Создание отзыва:             │
│ - appointment_id (PK)        │
│ - time = now()               │
│ - content                    │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Сохранение в БД              │
└──────────────────────────────┘
```

**Бизнес-правила**:
1. **Один отзыв на одну встречу** (1:1 relationship)
2. Отзыв привязан к встрече, а не к психологу напрямую
3. При удалении встречи отзыв удаляется (CASCADE)
4. Отзыв должен оставляться после завершения встречи (рекомендуется добавить проверку)

---

### 6. 🔐 Система ролей

#### Существующие роли

```python
class UserRole(enum.Enum):
    Therapist = "Therapist"          # Психолог
    Administrator = "Administrator"  # Администратор
```

#### Модель ролей

- Пользователь может иметь **несколько ролей** одновременно
- Роли хранятся в отдельной таблице (Many-to-Many через промежуточную таблицу)
- Composite Primary Key: (user_id, role)

#### Права доступа (рекомендуется реализовать)

| Роль | Права |
|------|-------|
| **Студент** (без ролей) | Просмотр психологов, создание записей, отмена своих записей, оставление отзывов |
| **Therapist** | Всё что студент + просмотр своих записей как терапевта, изменение статуса встреч |
| **Administrator** | Полный доступ ко всем функциям, управление пользователями, модерация |

**⚠️ Важно**: В текущей реализации проверка прав не полностью реализована. Рекомендуется добавить middleware для авторизации.

---

## Бизнес-правила и ограничения

### Пользователи

1. ✅ Email должен быть уникальным
2. ✅ Пароль минимум 8 символов
3. ✅ Пароль всегда хешируется (bcrypt)
4. ✅ Телефон в международном формате E164 (+79001234567)
5. ✅ Отчество и соцсети опциональны

### Записи на консультации

1. ✅ Пациент ≠ Терапевт (нельзя записаться к самому себе)
2. ✅ Оба пользователя должны существовать
3. ✅ Тип встречи: только Online или Offline
4. ✅ Статус по умолчанию: Accepted (принята психологом)
5. ✅ Venue обязательно: для Offline автоматически берется office терапевта
6. ✅ last_change_time автоматически обновляется
7. ✅ Проверка роли: терапевт должен иметь роль Therapist

### Психологи

1. ✅ ID психолога = ID пользователя
2. ✅ При удалении пользователя профиль психолога удаляется
3. ✅ Проверка роли Therapist реализована при создании записей

### Отзывы

1. ✅ Один отзыв на одну встречу
2. ✅ При удалении встречи отзыв удаляется

### Роли

1. ✅ Пользователь может иметь несколько ролей
2. ✅ Композитный ключ (user_id, role) - уникальность

---

## Валидация данных

### Уровни валидации

#### 1. Pydantic (Schemas)
- Формат email
- Формат телефона (E164)
- Длина строк
- Обязательные поля
- Типы данных

**Пример**:
```python
class UserCreateRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    phone_number: PhoneNumber
    password: str = Field(min_length=8, max_length=64)
```

#### 2. Service Layer
- Бизнес-правила
- Проверка существования связанных объектов
- Логические ограничения

**Пример**:
```python
if patient_id == therapist_id:
    raise ValueError("Нельзя записаться к самому себе")
```

#### 3. Database Layer
- Уникальность
- Foreign Key constraints
- NOT NULL constraints
- CASCADE правила

---

## Транзакции и целостность данных

### Использование транзакций

```python
async with get_async_db() as session:
    try:
        # Операции с БД
        await session.commit()
    except SQLAlchemyError:
        await session.rollback()
        raise
```

**Важно**:
- Все операции в одной сессии выполняются атомарно
- При ошибке происходит rollback
- Транзакции обеспечивают консистентность данных

### CASCADE удаление

При удалении пользователя автоматически удаляются:
- Все его роли
- Профиль психолога (если есть)
- Все встречи (как пациента и как терапевта)
- Отзывы о его встречах

---

## Безопасность

### Защита паролей

1. **Хеширование**: bcrypt с автоматической солью
2. **Никогда не возвращаем**: пароль не включается в API ответы
3. **Проверка**: только через bcrypt.verify()

### JWT токены

```python
{
  "sub": "user_id",           # Subject - ID пользователя
  "exp": 1697123456,          # Expiration time
  "iat": 1697037056           # Issued at
}
```

**Параметры**:
- Алгоритм: HS256 (HMAC-SHA256)
- Secret key: хранится в переменных окружения
- TTL: настраивается через ACCESS_TOKEN_EXPIRE

### HTTP-only Cookies

```python
response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,      # Защита от XSS
    secure=False,       # ⚠️ Для разработки! В продакшене True
    # samesite="None",  # ⚠️ Закомментировано для разработки
    expires=datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE)
)
```

---

## Реализованные возможности

1. ✅ **Логирование** - Полная система логирования с настраиваемыми уровнями
2. ✅ **Миграции БД** - Alembic для версионирования схемы
3. ✅ **Кастомные исключения** - Типизированная обработка ошибок в сервисном слое
4. ✅ **Структурированная архитектура** - Разделение на репозитории/сервисы/контроллеры
5. ✅ **Docker** - Контейнеризация приложения
6. ✅ **Makefile** - Автоматизация команд
7. ✅ **Пагинация** - Для списков психологов (skip/take)
8. ✅ **Eager loading** - Оптимизация запросов (joinedload/selectinload)

# Компоненты системы

## Обзор компонентов

Система состоит из следующих основных компонентов:

```
┌─────────────────────────────────────────────────┐
│                   FastAPI App                   │
│                  (main.py)                      │
└────────┬───────────────────────────┬────────────┘
         │                           │
         ▼                           ▼
┌─────────────────┐         ┌─────────────────────┐
│  API Routers    │         │   Middleware        │
│  (routes/)      │         │   (CORS, Auth)      │
└────────┬────────┘         └─────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│             Controllers (routes/controllers/)    │
│  ┌──────────┬──────────┬──────────┬──────────┐ │
│  │  Users   │  Appts   │Therapists│ Reviews  │ │
│  └──────────┴──────────┴──────────┴──────────┘ │
└────────┬────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│             Services (services/)                 │
│  ┌──────────┬──────────┬──────────┬──────────┐ │
│  │  Users   │  Appts   │Therapists│ Reviews  │ │
│  └──────────┴──────────┴──────────┴──────────┘ │
└────────┬────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│           Repositories (repositories/)           │
│  ┌──────────┬──────────┬──────────┬──────────┐ │
│  │  Users   │  Appts   │Therapists│ Reviews  │ │
│  └──────────┴──────────┴──────────┴──────────┘ │
└────────┬────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│              Models (models/)                    │
│  ┌──────────┬──────────┬──────────┬──────────┐ │
│  │  User    │Appointment│Therapist │ Review   │ │
│  └──────────┴──────────┴──────────┴──────────┘ │
└────────┬────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│              PostgreSQL Database                 │
└─────────────────────────────────────────────────┘
```

---

## 1. Main Application (main.py)

**Файл**: `psychohelp/main.py`

**Ответственность**:
- Создание и настройка FastAPI приложения
- Подключение роутеров
- Настройка CORS
- Инициализация логирования
- Инициализация БД при старте

### Инициализация логирования

```python
log_level = os.getenv("LOG_LEVEL", "DEBUG")
log_file_path = os.getenv("LOG_FILE")

setup_logging(
    level=log_level,
    log_file=Path(log_file_path) if log_file_path else None,
)

logger = get_logger(__name__)
```

**Особенности**:
- Логи настраиваются до создания приложения
- Уровень и путь файла конфигурируются через переменные окружения
- Логгер доступен во всех модулях приложения

### Основные функции

#### `get_application() -> FastAPI`
Создает и настраивает экземпляр приложения.

**Настройки**:
```python
application = FastAPI()
application.include_router(api_router)

# CORS Configuration
application.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://psychohelp.example.com",
        "https://185.128.105.126",
        "http://localhost:3000",
        "http://localhost:8000",
        # ... другие origins
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### `reset_database(engine: AsyncEngine) -> None`
Удаляет и пересоздает все таблицы БД.

```python
async def reset_database(engine: AsyncEngine) -> None:
    logger.warning("Resetting database - dropping all tables")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database reset completed")
```

**Логирование**:
- Warning при начале сброса БД
- Info после успешного завершения

#### Lifecycle Events
```python
@application.on_event("startup")
async def on_startup() -> None:
    logger.info("Starting application")
    if RESET_DB_ON_START:
        await reset_database(engine)
    logger.info("Application started successfully")

@application.on_event("shutdown")
async def on_shutdown() -> None:
    logger.info("Shutting down application")
```

#### `main() -> None`
Точка входа для запуска приложения.

```python
def main() -> None:
    uvicorn.run(
        "psychohelp.main:app",
        host="0.0.0.0",
        reload=True,
        log_config=None,  # Используем свою конфигурацию логов
        log_level=log_level.lower(),
    )
```

---

## 2. Configuration (config/)

### database.py

**Файл**: `psychohelp/config/database.py`

**Ответственность**:
- Конфигурация подключения к БД
- Управление сессиями
- Создание Base для ORM моделей

#### Config Class
```python
class Config:
    POSTGRES_USER = os.getenv("POSTGRES_USER", "myuser")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "mypassword")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "mydatabase")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = "5432"  # Фиксированный порт для Docker
    
    DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:..."
```

#### Async Session Manager
```python
@asynccontextmanager
async def get_async_db():
    session: AsyncSession = async_session()
    try:
        yield session
    except exc.SQLAlchemyError:
        await session.rollback()
        raise
    finally:
        await session.close()
```

**Использование**:
```python
async with get_async_db() as session:
    result = await session.execute(query)
```

---

### __init__.py

**Файл**: `psychohelp/config/__init__.py`

**Ответственность**:
- Экспорт глобальных настроек безопасности
- Конфигурация JWT токенов

#### Экспортируемые константы
```python
SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE = int(os.getenv("ACCESS_TOKEN_EXPIRE", 30))  # в минутах
```

**Использование**:
```python
from psychohelp.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE
```

---

### logging.py

**Файл**: `psychohelp/config/logging.py`

**Ответственность**:
- Настройка системы логирования приложения
- Конфигурация обработчиков логов
- Управление уровнями логирования

#### setup_logging()
Настраивает логирование для всего приложения.

**Параметры**:
- `level`: Уровень логирования (DEBUG, INFO, WARNING, ERROR)
- `log_file`: Опциональный путь к файлу логов
- `format_string`: Формат сообщений

**Особенности**:
- Логи выводятся в stdout
- Опционально в файл
- Подавляет verbose логи SQLAlchemy и Uvicorn

```python
setup_logging(
    level="DEBUG",
    log_file=Path("/path/to/logs.log"),
)
```

#### get_logger()
Возвращает логгер для модуля.

```python
logger = get_logger(__name__)
logger.info("Application started")
logger.error("Error occurred", exc_info=True)
```

**Использование в коде**:
```python
from psychohelp.config.logging import get_logger

logger = get_logger(__name__)
logger.info("Processing request")
```

---

## 3. Models (models/)

ORM модели, представляющие таблицы БД.

### users.py

**Класс**: `User`

**Описание**: Базовая модель пользователя

**Ключевые поля**:
- `id`: UUID (Primary Key)
- `first_name`, `middle_name`, `last_name`: ФИО пользователя
- `email`: Email (unique, nullable=True) - используется для входа
- `phone_number`: Телефон в формате E164 (обязательно)
- `password`: Хешированный пароль (bcrypt, обязательно)
- `social_media`: Ссылки на соцсети (nullable=True)

**Relationships**:
```python
roles = relationship("Role", back_populates="user")
appointments_as_patient = relationship("Appointment", foreign_keys="[Appointment.patient_id]")
appointments_as_therapist = relationship("Appointment", foreign_keys="[Appointment.therapist_id]")
therapist_info = relationship("Therapist", uselist=False)  # One-to-One
```

---

### therapists.py

**Класс**: `Therapist`

**Описание**: Расширенная информация о психологах

**Особенности**:
- `id` - Foreign Key к `users.id` и Primary Key одновременно
- One-to-One relationship с User
- CASCADE удаление при удалении User

**Ключевые поля**:
- `experience`: Опыт работы
- `qualification`: Квалификация и сертификаты
- `consult_areas`: Области консультирования
- `education`: Образование
- `office`: Номер кабинета
- `description`: Полное описание
- `short_description`: Краткое описание
- `photo`: Путь к фото (опционально)

**Relationships**:
```python
user = relationship("User", back_populates="therapist_info")
```

---

### appointments.py

**Класс**: `Appointment`

**Описание**: Записи на консультации

**Enum Types**:
```python
class AppointmentType(enum.Enum):
    Offline = "Offline"  # Очная встреча
    Online = "Online"    # Онлайн-консультация

class AppointmentStatus(enum.Enum):
    Approved = "Approved"    # Одобрена (создана)
    Accepted = "Accepted"    # Принята психологом
    Cancelled = "Cancelled"  # Отменена
    Done = "Done"            # Завершена
```

**Ключевые поля**:
- `id`: UUID (Primary Key)
- `patient_id`, `therapist_id`: Foreign Keys к users
- `type`: Тип встречи (Online/Offline)
- `status`: Статус записи
- `reason`: Причина обращения (опционально)
- `remind_time`: Время напоминания (опционально)
- `last_change_time`: Время последнего изменения
- `venue`: Место встречи (кабинет/ссылка)

**Relationships**:
```python
patient = relationship("User", foreign_keys=[patient_id], back_populates="appointments_as_patient")
therapist = relationship("User", foreign_keys=[therapist_id], back_populates="appointments_as_therapist")
review = relationship("Review", uselist=False)  # One-to-One
```

**Каскадное удаление**: При удалении User удаляются все его записи (как пациента и как терапевта)

---

### reviews.py

**Класс**: `Review`

**Описание**: Отзывы о консультациях

**Особенности**:
- `appointment_id` как Primary Key
- One-to-One с Appointment
- CASCADE удаление при удалении Appointment

**Ключевые поля**:
- `appointment_id`: UUID (Primary Key, Foreign Key к appointments)
- `time`: Время создания отзыва
- `content`: Содержание отзыва

**Relationships**:
```python
appointment = relationship("Appointment", back_populates="review")
```

---

### roles.py

**Класс**: `Role`

**Описание**: Роли пользователей

**Enum Type**:
```python
class UserRole(enum.Enum):
    Therapist = "Therapist"          # Психолог
    Administrator = "Administrator"  # Администратор
```

**Ключевые поля**:
- `user_id`: UUID (часть составного Primary Key, Foreign Key к users)
- `role`: Enum (часть составного Primary Key)

**Особенности**:
- Composite Primary Key: (user_id, role)
- Один пользователь может иметь несколько ролей
- Many-to-Many relationship через эту таблицу
- CASCADE удаление при удалении User

**Relationships**:
```python
user = relationship("User", back_populates="roles")
```

---

## 4. Repositories (repositories/)

Слой доступа к данным. Все взаимодействия с БД инкапсулированы здесь.

### Общие паттерны

#### CRUD операции
Каждый репозиторий реализует базовые операции:
- `create_*` - создание
- `get_*_by_id` - получение по ID
- `get_*_by_*` - получение по другим параметрам
- `update_*` - обновление
- `delete_*` - удаление

#### Использование AsyncSession
```python
async with get_async_db() as session:
    result = await session.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()
    return user
```

---

### repositories/__init__.py

**Утилиты безопасности**:

#### `create_access_token(sub: str) -> str`
Создает JWT токен.

**Параметры**:
- `sub`: User ID (subject)
- `exp`: Время истечения
- `iat`: Время выдачи

```python
encoded = jwt.encode(
    {"sub": str(sub), "exp": expire, "iat": now},
    SECRET_KEY,
    algorithm=ALGORITHM,
)
```

#### `get_user_id_from_token(token: str) -> UUID`
Декодирует токен и извлекает User ID.

**Проверки**:
- Подпись
- Время истечения
- Время выдачи

#### `hash_password(password: str) -> str`
Хеширует пароль с использованием bcrypt.

#### `verify_password(plain: str, hashed: str) -> bool`
Проверяет пароль.

---

### repositories/users.py

**Основные функции**:

#### `create_user(...) -> User`
Создает нового пользователя.

**Валидация**:
- Проверка уникальности email
- Хеширование пароля должно быть выполнено до вызова

#### `get_user_by_id(user_id: UUID) -> User | None`
Получает пользователя по ID.

#### `get_user_by_email(email: str) -> User | None`
Получает пользователя по email.

#### `get_user_by_token(token: str) -> User | None`
Получает пользователя по JWT токену.

**Процесс**:
1. Декодирует токен
2. Извлекает user_id
3. Загружает пользователя из БД

---

### repositories/appointments.py

**Основные функции**:

#### `create_appointment(...) -> Appointment`
Создает новую запись.

**Автоматические поля**:
- `id`: генерируется UUID
- `status`: устанавливается "Approved"
- `last_change_time`: текущее время

#### `get_appointment_by_id(id: UUID) -> Appointment | None`
Получает запись по ID.

#### `get_appointments_by_user_id(user_id: UUID) -> list[Appointment]`
Получает все записи пользователя (как пациент и как терапевт).

**Запрос**:
```python
appointments = await session.execute(
    select(Appointment).where(
        (Appointment.patient_id == user_id) | 
        (Appointment.therapist_id == user_id)
    )
)
```

#### `cancel_appointment(id: UUID) -> None`
Отменяет запись.

**Действия**:
1. Находит запись
2. Проверяет статус
3. Устанавливает status = "Cancelled"
4. Обновляет last_change_time

---

### repositories/therapists.py

**Основные функции**:

#### `get_therapist_by_id(id: UUID) -> Therapist | None`
Получает информацию о психологе с eager loading данных пользователя.

**Особенности**:
- Использует `selectinload` для загрузки связи с User

#### `get_therapists(skip: int = 0, take: int = 10) -> list[Therapist]`
Получает список психологов с пагинацией.

**Параметры**:
- `skip` - Offset для пагинации (по умолчанию 0)
- `take` - Limit для пагинации (по умолчанию 10)

**Особенности**:
- Использует `joinedload` для оптимизации загрузки User данных
- Поддерживает пагинацию через offset/limit
- Документирован комментарием в коде

**Реализовано**:
- ✅ Пагинация
- ✅ Eager loading (joinedload)

---

### repositories/reviews.py

**Основные функции**:

#### `get_review_by_appointment_id(id: UUID) -> Review | None`
Получает отзыв о встрече.

---

### repositories/roles.py

**Основные функции**:

#### `get_roles_by_user_id(user_id: UUID) -> list[Role]`
Получает все роли пользователя.

---

## 5. Services (services/)

Бизнес-логика приложения. Координирует работу репозиториев и применяет бизнес-правила.

### Паттерн использования

```
Controller → Service → Repository → Database
```

**Преимущества**:
- Разделение ответственности
- Переиспользование логики
- Упрощение тестирования
- Легкость добавления сложной логики

---

### services/users/

**Структура**: Модуль разделен на несколько файлов для лучшей организации кода.

#### services/users/users.py

**Основные функции**:

##### `register_user(...) -> tuple[User, str]`
Регистрирует нового пользователя.

**Процесс**:
1. Хеширует пароль
2. Создает пользователя через репозиторий
3. Генерирует JWT токен
4. Возвращает (user, token)

**Бизнес-логика**:
- Автоматическое хеширование пароля
- Генерация токена для автоматической аутентификации

##### `login_user(email: str, password: str) -> UserWithToken`
Аутентифицирует пользователя.

**Процесс**:
1. Получает пользователя по email
2. Проверяет пароль
3. Генерирует токен
4. Возвращает `UserWithToken` или выбрасывает исключение

**Бизнес-логика**:
- Проверка пароля через bcrypt
- Выбрасывает `UserNotFound` если пользователь не найден
- Выбрасывает `WrongPassword` если пароль неверный

**Исключения**:
```python
raise exceptions.UserNotFound()  # Пользователь не найден
raise exceptions.WrongPassword()  # Неверный пароль
```

##### `get_user_by_*(...) -> User | None`
Прокси-функции к репозиторию.

**Цель**: Единая точка доступа к данным пользователей

#### services/users/exceptions.py

**Кастомные исключения**:

```python
class UserNotFound(Exception):
    """Выбрасывается, когда пользователь не найден"""
    pass

class WrongPassword(Exception):
    """Выбрасывается при неверном пароле"""
    pass
```

**Использование**:
Позволяет контроллерам обрабатывать ошибки более специфично.

#### services/users/models.py

**Модели данных для сервисного слоя**:

```python
@dataclass(frozen=True, slots=True)
class UserWithToken:
    user: models.User
    token: str
```

**Назначение**: Типобезопасная передача данных между слоями приложения.

---

### services/appointments.py

**Основные функции**:

#### `create_appointment(...) -> Appointment`
Создает новую запись.

**Бизнес-логика**:
1. Проверяет, что пациент ≠ терапевт
2. Устанавливает статус "Approved"
3. Устанавливает текущее время в last_change_time
4. Устанавливает venue (если не указано)

**Валидация**:
```python
if patient_id == therapist_id:
    raise ValueError("Пациент не может быть терапевтом")
```

#### `cancel_appointment_by_id(id: UUID) -> None`
Отменяет запись.

**Бизнес-логика**:
1. Проверяет существование записи
2. Проверяет, что статус не "Cancelled" или "Done"
3. Обновляет статус и время

#### `get_appointments_by_token(token: str) -> list[Appointment]`
Получает записи текущего пользователя.

**Процесс**:
1. Декодирует токен
2. Извлекает user_id
3. Получает все записи пользователя

---

### services/therapists.py

**Основные функции**:

#### `get_therapist_by_id(id: UUID) -> dict | None`
Получает информацию о психологе с данными пользователя.

**Возвращает**: Словарь с данными психолога и пользователя или None.

**Поля**:
- Все поля из Therapist модели
- Данные пользователя (first_name, middle_name, last_name, phone_number, email)

#### `get_therapists(skip: int = 0, take: int = 10) -> list[dict]`
Получает список психологов с пагинацией.

**Параметры**:
- `skip` - Количество записей для пропуска (offset)
- `take` - Количество записей для возврата (limit)

**Возвращает**: Список словарей с данными психологов.

**Особенности**:
- Использует `joinedload` для загрузки связанных данных пользователя
- Возвращает словари вместо ORM объектов для удобства сериализации
- Поддержка пагинации (skip/take)
- Eager loading связанных данных

---

### services/reviews.py

**Основные функции**:

#### `get_review_by_appointment_id(id: UUID) -> Review | None`
Получает отзыв о встрече.

---

### services/roles.py

**Основные функции**:

#### `get_roles_by_user_id(user_id: UUID) -> list[Role]`
Получает роли пользователя.

---

## 6. Routes/Controllers (routes/controllers/)

API endpoints. Обрабатывают HTTP запросы и формируют ответы.

### Общие паттерны

#### Структура контроллера
```python
router = APIRouter(prefix="/resource", tags=["resource"])

@router.get("/{id}")
async def get_resource(id: UUID):
    resource = await service.get_resource(id)
    if not resource:
        raise HTTPException(404, detail="Not found")
    return resource
```

#### Обработка ошибок
```python
try:
    result = await service.create_resource(...)
except ValueError as e:
    raise HTTPException(400, detail=str(e))
```

---

### routes/controllers/__init__.py

**Утилиты**:

#### `set_token_in_cookie(response: Response, token: str)`
Устанавливает JWT токен в HTTP-only cookie.

**Параметры cookie**:
```python
response.set_cookie(
    key="access_token",
    value=token,
    expires=datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE),
    httponly=True,
    secure=False,  # Для разработки, в продакшене должно быть True
    # samesite="None",  # Закомментировано для разработки
)
```

---

### routes/controllers/users.py

**Router**: `/users`

**Endpoints**:
- `GET /user` - Текущий пользователь (требует аутентификации)
- `GET /user/{id}` - По ID
- `POST /register` - Регистрация
- `POST /login` - Вход
- `POST /logout` - Выход

**Особенности**:
- Cookie-based authentication
- Валидация через Pydantic
- Разделение публичных и защищенных endpoints
- Логирование через `get_logger(__name__)`
- Обработка кастомных исключений из сервисного слоя

**Обработка ошибок**:
```python
# При регистрации
except ValueError as exc:
    raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

# При входе
except (users_exceptions.UserNotFound, users_exceptions.WrongPassword):
    raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Неверные данные")
```

**Статус-коды**:
- `200 OK` - Успешный вход/выход
- `201 CREATED` - Успешная регистрация
- `401 UNAUTHORIZED` - Пользователь не авторизован
- `403 FORBIDDEN` - Неверные учетные данные
- `404 NOT_FOUND` - Пользователь не найден
- `422 UNPROCESSABLE_ENTITY` - Ошибка валидации

---

### routes/controllers/appointments.py

**Router**: `/appointments`

**Endpoints**:
- `GET /` - Все записи пользователя
- `GET /{id}` - По ID
- `POST /create` - Создание
- `PUT /{id}/cancel` - Отмена

**Особенности**:
- Опциональная аутентификация на некоторых endpoints
- Query параметры для фильтрации

---

### routes/controllers/therapists.py

**Router**: `/therapists`

**Endpoints**:
- `GET /` - Список психологов с пагинацией
- `GET /{id}` - Психолог по ID

**Параметры пагинации**:
```
GET /therapists?skip=0&take=10
```
- `skip` (int, ≥0, по умолчанию 0) - Сколько записей пропустить
- `take` (int, >0, по умолчанию 10) - Сколько записей вернуть

**Особенности**:
- Возвращает 404, если психологи не найдены
- Логирование всех операций
- Использует `joinedload` для загрузки связанных данных пользователя

**Примеры**:
```bash
# Первые 10 психологов
GET /therapists

# Следующие 10 психологов
GET /therapists?skip=10&take=10

# Первые 5 психологов
GET /therapists?skip=0&take=5
```

---

### routes/controllers/reviews.py

**Router**: `/reviews`

**Endpoints**:
- `GET /{review_id}` - Отзыв по ID

---

### routes/controllers/roles.py

**Router**: `/roles`

**Endpoints**:
- `GET /{user_id}` - Получить роли пользователя
- `PUT /{user_id}` - Добавить роли пользователю (body: list[UserRole])
- `DELETE /{user_id}` - Удалить роли у пользователя (body: list[UserRole])

**Особенности**:
- Все операции требуют user_id
- PUT и DELETE принимают список ролей в теле запроса
- При пустом списке ролей возвращается 400 Bad Request
- При ошибке возвращается 500 Internal Server Error

**Пример использования**:
```json
PUT /roles/{user_id}
Body: ["Therapist", "Administrator"]

DELETE /roles/{user_id}
Body: ["Administrator"]
```

---

### routes/controllers/images.py

**Router**: `/images`

**Endpoints**:
- `POST /upload` - Загрузка изображения
- `GET /{filename}` - Получение изображения

**Особенности**:
- Работа с multipart/form-data
- Сохранение файлов на сервере

---

## 7. Schemas (schemas/)

Pydantic модели для валидации и сериализации.

### Типы схем

#### Request Schemas
Для входящих данных (POST/PUT).

**Пример**:
```python
class UserCreateRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)
```

#### Response Schemas
Для исходящих данных (GET).

**Пример**:
```python
class UserResponse(BaseModel):
    id: UUID
    first_name: str
    email: EmailStr
    
    class Config:
        from_attributes = True  # Для ORM моделей
```

#### Base Schemas
Полные модели с всеми полями.

---

### schemas/users.py

**Модели**:
- `UserCreateRequest` - Для регистрации
- `UserBase` - Полная модель с password
- `UserResponse` - Для ответов (без пароля)
- `LoginRequest` - Для входа
- `TokenResponse` - Ответ с токеном

**Валидаторы**:
- `EmailStr` - Pydantic email validator (nullable в схеме)
- `PhoneNumber` - Валидатор для E164 формата (из pydantic-extra-types)

**Настройки PhoneNumber**:
```python
PhoneNumber.phone_format = "E164"  # Формат +79001234567
PhoneNumber.default_region_code = "+7"  # Россия по умолчанию
```

**Особенности**:
- `email` опциональный (`EmailStr | None`)
- `middle_name` опциональный (`str | None`)
- `social_media` опциональный (`str | None`)
- Пароль минимум 8, максимум 256 символов

---

### schemas/appointments.py

**Модели**:
- `AppointmentBase` - Полная модель для ответов
- `AppointmentCreateRequest` - Для создания записи

**Enum импорты**:
```python
from psychohelp.repositories.appointments import (
    AppointmentType,
    AppointmentStatus,
)
```

**Особенности**:
- `venue` может быть опциональным при создании (None для Offline)
- `reason` опциональный
- `remind_time` опциональный

---

## 8. Tests (tests/)

Тесты для проверки функциональности.

### conftest.py

**Фикстуры**:
- Настройка тестовой БД
- Создание тестового клиента
- Моки зависимостей

### test_users.py

Тесты для пользовательских операций:
- Регистрация
- Вход
- Получение данных

---

## Взаимодействие компонентов

### Пример: Создание записи

```
1. HTTP Request
   POST /appointments/create
   Body: {patient_id, therapist_id, ...}

2. Controller (routes/controllers/appointments.py)
   - Получает Request Body
   - Валидирует через AppointmentCreateRequest
   - Вызывает service.create_appointment()

3. Service (services/appointments.py)
   - Применяет бизнес-правила
   - Проверяет patient_id ≠ therapist_id
   - Вызывает repository.create_appointment()

4. Repository (repositories/appointments.py)
   - Создает объект Appointment
   - Сохраняет в БД через SQLAlchemy
   - Возвращает созданный объект

5. Service
   - Получает результат
   - Возвращает в Controller

6. Controller
   - Сериализует через AppointmentBase
   - Возвращает HTTP Response
```

---

## Конфигурация и окружение

### Переменные окружения

```bash
# Database
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=mydatabase
POSTGRES_HOST=localhost
# POSTGRES_PORT фиксирован на 5432 в коде

# Application
RESET_DB_ON_START=false
RESET_COOKIE_ON_START=true
APP_PORT=8000

# Logging
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
LOG_FILE=/path/to/logs.log  # Опционально

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE=30  # минуты (по умолчанию 30)
```

**Значения по умолчанию**:
- `POSTGRES_*`: Значения для локальной разработки
- `RESET_DB_ON_START`: `false` (не сбрасывать БД при старте)
- `RESET_COOKIE_ON_START`: `true` (сбрасывать cookie)
- `LOG_LEVEL`: `DEBUG`
- `ACCESS_TOKEN_EXPIRE`: `30` минут (не 1440!)

### Docker

**Dockerfile**:
- Base: Python 3.13-slim
- Package manager: uv
- Workdir: /app

**docker-compose.yml**:
- Service `app`: FastAPI приложение
- Service `db`: PostgreSQL 17
- Volume для данных БД
