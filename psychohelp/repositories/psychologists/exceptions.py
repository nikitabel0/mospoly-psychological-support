class UserNotFoundForPsychologistException(Exception):
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(f"User with ID {user_id} not found")


class PsychologistRoleNotFoundException(Exception):
    def __init__(self):
        super().__init__("Role 'psychologist' not found in database")


class PsychologistNotFoundException(Exception):
    def __init__(self, psychologist_id):
        self.psychologist_id = psychologist_id
        super().__init__(f"Psychologist with ID {psychologist_id} not found")


class PsychologistAlreadyExistsException(Exception):
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(f"Psychologist for user {user_id} already exists")
