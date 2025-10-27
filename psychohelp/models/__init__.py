# Импортируем все модели для регистрации в SQLAlchemy
from .users import User
from .therapists import Therapist
from .appointments import Appointment, AppointmentType, AppointmentStatus
from .reviews import Review
from .roles import Role, UserRole

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
