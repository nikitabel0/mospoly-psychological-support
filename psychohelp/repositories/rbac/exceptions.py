"""
Исключения для модуля RBAC
"""


class RBACException(Exception):
    """Базовое исключение для RBAC"""
    pass


class UserNotFoundException(RBACException):
    """Пользователь не найден"""
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(f"User with ID {user_id} not found")


class RoleNotFoundException(RBACException):
    """Роль не найдена"""
    def __init__(self, role_code: str):
        self.role_code = role_code
        super().__init__(f"Role '{role_code}' not found")


class PermissionNotFoundException(RBACException):
    """Право доступа не найдено"""
    def __init__(self, permission_code: str):
        self.permission_code = permission_code
        super().__init__(f"Permission '{permission_code}' not found")


class RoleAlreadyAssignedException(RBACException):
    """Роль уже назначена пользователю"""
    def __init__(self, user_id, role_code: str):
        self.user_id = user_id
        self.role_code = role_code
        super().__init__(f"Role '{role_code}' is already assigned to user {user_id}")


class RoleNotAssignedException(RBACException):
    """Роль не назначена пользователю"""
    def __init__(self, user_id, role_code: str):
        self.user_id = user_id
        self.role_code = role_code
        super().__init__(f"Role '{role_code}' is not assigned to user {user_id}")

