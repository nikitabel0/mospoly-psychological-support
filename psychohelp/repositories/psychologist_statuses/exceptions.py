class OverlappingStatusException(Exception):
    def __init__(self, psychologist_id):
        self.psychologist_id = psychologist_id
        super().__init__(f"Psychologist with ID {psychologist_id} has overlapping status")

class InvalidStatusPeriodException(Exception):
    def __init__(self, psychologist_id):
        self.psychologist_id = psychologist_id
        super().__init__(f"Psychologist with ID {psychologist_id} has an invalid status period")

class PsychologistStatusNotFoundException(Exception):
    def __init__(self, psychologist_id):
        self.psychologist_id = psychologist_id
        super().__init__(f"Psychologist with ID {psychologist_id} has no status found")

class PsychologistStatusNotFound(Exception):
    def __init__(self, status_id):
        self.status_id = status_id
        super().__init__(f"Status with ID {status_id} not found")

class UserIsNotPsychologist(Exception):
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(f"User with ID {user_id} is not an psychologist")