from psychohelp.constants.rbac import RoleCode


class UserNotFoundException(Exception):
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(f"User with ID {user_id} not found")


class RoleNotFoundException(Exception):
    def __init__(self, role_code: RoleCode):
        self.role_code = role_code
        super().__init__(f"Role '{role_code.value}' not found")
