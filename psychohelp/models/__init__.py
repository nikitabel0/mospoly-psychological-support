# Импортируем все модели для регистрации в SQLAlchemy
from .appointments import Appointment, AppointmentStatus, AppointmentType
from .reviews import Review
from .roles import Role, UserRole
from .therapists import Therapist
from .users import User

__all__ = [
    "User",
    "Therapist",
    "Appointment",
    "AppointmentType",
    "AppointmentStatus",
    "Review",
    "Role",
    "UserRole",
]
