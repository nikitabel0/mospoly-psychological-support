"""
Исключения для модуля appointments
"""


class AppointmentException(Exception):
    """Базовое исключение для записей на прием"""
    pass


class PatientNotFoundException(AppointmentException):
    """Пациент не найден"""
    def __init__(self, patient_id):
        self.patient_id = patient_id
        super().__init__(f"Пациент с ID {patient_id} не найден")


class TherapistNotFoundException(AppointmentException):
    """Психолог не найден"""
    def __init__(self, therapist_id):
        self.therapist_id = therapist_id
        super().__init__(f"Психолог с ID {therapist_id} не найден")


class TherapistRoleNotFoundException(AppointmentException):
    """Пользователь не имеет роли психолога"""
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(f"Пользователь с ID {user_id} не имеет роли психолога")


class VenueRequiredException(AppointmentException):
    """Место встречи не указано для онлайн консультации"""
    def __init__(self):
        super().__init__("Место для онлайн встречи не указано")


class InvalidScheduledTimeException(AppointmentException):
    """Время записи указано некорректно"""
    def __init__(self, scheduled_time):
        self.scheduled_time = scheduled_time
        super().__init__(f"Время записи {scheduled_time} не может быть в прошлом")


class InvalidRemindTimeException(AppointmentException):
    """Время напоминания указано некорректно"""
    def __init__(self, remind_time, reason: str):
        self.remind_time = remind_time
        self.reason = reason
        super().__init__(f"Некорректное время напоминания {remind_time}: {reason}")


class AppointmentNotFoundException(AppointmentException):
    """Запись на прием не найдена"""
    def __init__(self, appointment_id):
        self.appointment_id = appointment_id
        super().__init__(f"Запись на прием с ID {appointment_id} не найдена")


class AppointmentAlreadyCancelledException(AppointmentException):
    """Запись уже отменена"""
    def __init__(self, appointment_id):
        self.appointment_id = appointment_id
        super().__init__(f"Запись на прием с ID {appointment_id} уже отменена")

