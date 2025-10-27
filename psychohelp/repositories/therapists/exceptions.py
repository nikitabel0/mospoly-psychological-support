"""
Исключения для модуля therapists
"""


class TherapistException(Exception):
    """Базовое исключение для терапевтов"""
    pass


class UserNotFoundForTherapistException(TherapistException):
    """Пользователь не найден при создании терапевта"""
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(f"User with ID {user_id} not found")


class PsychologistRoleNotFoundException(TherapistException):
    """Роль 'psychologist' не найдена в базе данных"""
    def __init__(self):
        super().__init__("Role 'psychologist' not found in database")


class TherapistNotFoundException(TherapistException):
    """Терапевт не найден"""
    def __init__(self, therapist_id):
        self.therapist_id = therapist_id
        super().__init__(f"Therapist with ID {therapist_id} not found")


class TherapistAlreadyExistsException(TherapistException):
    """Терапевт для данного пользователя уже существует"""
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(f"Therapist for user {user_id} already exists")

