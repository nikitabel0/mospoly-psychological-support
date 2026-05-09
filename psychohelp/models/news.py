import uuid
import enum

from sqlalchemy import Column, String, Text, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from psychohelp.config.config import Base


# Создаем список доступных типов новостей
class NewsType(str, enum.Enum):
    ANNOUNCEMENT = 'Анонс мероприятия'
    REPORT = 'Отчет о мероприятии'


class News(Base):
    __tablename__ = "news"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    slug = Column(String(255), unique=True, index=True, nullable=False, comment="Уникальный URL")

    image = Column(String(1024), nullable=True, comment="Ссылка на картинку")
    type = Column(Enum(NewsType), nullable=True, comment="Тип новости")

    date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    event_date = Column(DateTime(timezone=True), nullable=False, comment="Дата мероприятия")

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    link = Column(String(1024), nullable=True)
    text = Column(Text, nullable=True)