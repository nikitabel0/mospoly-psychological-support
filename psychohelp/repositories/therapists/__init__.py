"""
Репозиторий для работы с терапевтами
"""

from uuid import UUID

from .therapists import (
    get_therapist_by_id,
    get_therapists,
    create_therapist,
    delete_therapist,
)

from .exceptions import (
    TherapistException,
    UserNotFoundForTherapistException,
    PsychologistRoleNotFoundException,
    TherapistNotFoundException,
    TherapistAlreadyExistsException,
)

__all__ = [
    "get_therapist_by_id",
    "get_therapists",
    "create_therapist",
    "delete_therapist",
    "UUID",
    "TherapistException",
    "UserNotFoundForTherapistException",
    "PsychologistRoleNotFoundException",
    "TherapistNotFoundException",
    "TherapistAlreadyExistsException",
]

