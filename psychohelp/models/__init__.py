# Импортируем все модели для регистрации в SQLAlchemy
from .users import User
from .therapists import Therapist
from .appointments import Appointment, AppointmentType, AppointmentStatus
from .reviews import Review
from .roles import Role, roles_permissions, users_roles
from .permissions import Permission

__all__ = [
    "User",
    "Therapist", 
    "Appointment",
    "AppointmentType",
    "AppointmentStatus",
    "Review",
    "Role",
    "Permission",
    "roles_permissions",
    "users_roles",
]
