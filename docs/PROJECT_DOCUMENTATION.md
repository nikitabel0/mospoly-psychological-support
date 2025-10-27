# Документация проекта "Психологическая служба МосПоли"

## Содержание

1. [Обзор проекта](#обзор-проекта-психологическая-служба-мосполи)
2. [Бизнес-логика системы](#бизнес-логика-системы)
3. [Компоненты системы](#компоненты-системы)

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
4. **Безопасность** - защита персональных данных
5. **Гибкость** - поддержка онлайн и офлайн форматов
6. **Аналитика** - возможность анализа загруженности службы


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
2. **Статус по умолчанию**: `Approved` (одобрена)
3. **Venue обязательно**: для Online - ссылка, для Offline - кабинет
4. **last_change_time**: автоматически устанавливается при создании
5. Причина обращения опциональна (конфиденциальность)

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
4. ✅ Статус по умолчанию: Approved
5. ✅ Venue обязательно для создания
6. ✅ last_change_time автоматически обновляется
7. ⚠️ Нет проверки на двойное бронирование одного времени
8. ⚠️ Нет проверки доступности психолога

### Психологи

1. ✅ ID психолога = ID пользователя
2. ✅ При удалении пользователя профиль психолога удаляется
3. ⚠️ Нет автоматической проверки наличия роли Therapist

### Отзывы

1. ✅ Один отзыв на одну встречу
2. ✅ При удалении встречи отзыв удаляется
3. ⚠️ Нет проверки, что встреча завершена
4. ⚠️ Нет проверки, что отзыв оставляет пациент

### Роли

1. ✅ Пользователь может иметь несколько ролей
2. ✅ Композитный ключ (user_id, role) - уникальность
3. ⚠️ Нет автоматической проверки прав доступа

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
    secure=True,        # Только HTTPS (prod)
    samesite="None",    # CORS support
    expires=...
)
```

---

## Рекомендуемые улучшения

### Критичные

1. ✅ **Проверка прав доступа** - middleware для авторизации
2. ✅ **Проверка статуса встречи** - перед созданием отзыва
3. ✅ **Проверка двойного бронирования** - один психолог, одно время
4. ✅ **Rate limiting** - защита от спама и атак

### Желательные

1. 📧 **Email уведомления** - о создании/отмене записей
2. 🔔 **Push уведомления** - напоминания о встречах
3. 📊 **Логирование** - аудит всех действий
4. 🔍 **Поиск и фильтрация** - психологов по специализации
5. ⭐ **Рейтинги** - система оценок психологов

### Технические

1. 🗄️ **Миграции БД** - Alembic для версионирования схемы
2. 🔄 **Кэширование** - Redis для часто запрашиваемых данных
3. 📈 **Мониторинг** - метрики производительности
4. 🧪 **Тесты** - покрытие бизнес-логики тестами

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
- Инициализация БД при старте

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
    allow_origins=[...],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### `reset_database(engine: AsyncEngine)`
Удаляет и пересоздает все таблицы БД.

**⚠️ Внимание**: Используется только для разработки!

```python
async def reset_database(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
```

#### Startup Event
```python
@application.on_event("startup")
async def on_startup():
    if RESET_DB_ON_START:
        await reset_database(engine)
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
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    
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

## 3. Models (models/)

ORM модели, представляющие таблицы БД.

### users.py

**Класс**: `User`

**Описание**: Базовая модель пользователя

**Ключевые поля**:
- `id`: UUID (Primary Key)
- `first_name`, `middle_name`, `last_name`: ФИО пользователя
- `email`: Уникальный email для входа
- `phone_number`: Телефон в формате E164
- `password`: Хешированный пароль (bcrypt)
- `social_media`: Ссылки на соцсети (опционально)

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
Получает информацию о психологе.

#### `get_all_therapists() -> list[Therapist]`
Получает список всех психологов.

**Может использоваться с**:
- Фильтрацией
- Пагинацией (будущее улучшение)
- Сортировкой

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

### services/users.py

**Основные функции**:

#### `register_user(...) -> tuple[User, str]`
Регистрирует нового пользователя.

**Процесс**:
1. Хеширует пароль
2. Создает пользователя через репозиторий
3. Генерирует JWT токен
4. Возвращает (user, token)

**Бизнес-логика**:
- Автоматическое хеширование пароля
- Генерация токена для автоматической аутентификации

#### `login_user(email: str, password: str) -> tuple[User, str] | None`
Аутентифицирует пользователя.

**Процесс**:
1. Получает пользователя по email
2. Проверяет пароль
3. Генерирует токен
4. Возвращает (user, token) или None

**Бизнес-логика**:
- Проверка пароля через bcrypt
- Возврат None при неверных данных

#### `get_user_by_*(...) -> User | None`
Прокси-функции к репозиторию.

**Цель**: Единая точка доступа к данным пользователей

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

#### `get_therapist_by_id(id: UUID) -> Therapist | None`
Получает информацию о психологе.

#### `get_all_therapists() -> list[Therapist]`
Получает список всех психологов.

**Возможные улучшения**:
- Кэширование результатов
- Фильтрация по специализации
- Сортировка по рейтингу

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
    expires=...,
    httponly=True,
    secure=True,
    samesite="None",
)
```

---

### routes/controllers/users.py

**Router**: `/users`

**Endpoints**:
- `GET /user` - Текущий пользователь
- `GET /user/{id}` - По ID или email
- `POST /register` - Регистрация
- `POST /login` - Вход
- `POST /logout` - Выход

**Особенности**:
- Cookie-based authentication
- Валидация через Pydantic
- Разделение публичных и защищенных endpoints

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
- `GET /` - Все психологи
- `GET /{id}` - По ID

---

### routes/controllers/reviews.py

**Router**: `/reviews`

**Endpoints**:
- `GET /{appointment_id}` - Отзыв о встрече

---

### routes/controllers/roles.py

**Router**: `/roles`

**Endpoints**:
- `GET /{user_id}` - Роли пользователя

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
- `UserResponse` - Для ответов (без пароля)
- `LoginRequest` - Для входа
- `TokenResponse` - Ответ с токеном

**Валидаторы**:
- `EmailStr` - Pydantic email validator
- `PhoneNumber` - Кастомный валидатор для E164 формата

---

### schemas/appointments.py

**Модели**:
- `AppointmentCreateRequest` - Для создания
- `AppointmentBase` - Полная модель

**Enum импорты**:
```python
from psychohelp.repositories.appointments import (
    AppointmentType,
    AppointmentStatus,
)
```

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
POSTGRES_PORT=5432

# Application
RESET_DB_ON_START=false
RESET_COOKIE_ON_START=true
APP_PORT=8000

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE=1440  # minutes
```

### Docker

**Dockerfile**:
- Base: Python 3.13-slim
- Package manager: uv
- Workdir: /app

**docker-compose.yml**:
- Service `app`: FastAPI приложение
- Service `db`: PostgreSQL 17
- Volume для данных БД

---

## Зависимости

### Основные (pyproject.toml)

- **FastAPI** 0.115.0 - Web framework
- **Uvicorn** - ASGI server
- **SQLAlchemy** 2.0.35 - ORM
- **asyncpg** 0.30.0 - PostgreSQL driver
- **Pydantic** 2+ - Валидация
- **PyJWT** 2.9.0 - JWT токены
- **Passlib[bcrypt]** - Хеширование паролей
- **Phonenumbers** - Валидация телефонов

### Dev зависимости

- **pytest** - Тестирование
- **pytest-asyncio** - Async тесты

---
