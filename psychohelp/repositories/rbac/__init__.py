"""
Репозиторий для работы с RBAC (ролями и правами доступа)
"""

from uuid import UUID

from .rbac import (
    get_user_roles,
    get_user_permissions,
    get_role_by_code,
    get_all_roles,
    assign_role_to_user,
    remove_role_from_user,
    get_permission_by_code,
    get_all_permissions,
    get_permissions_by_resource,
)

from .exceptions import (
    RBACException,
    UserNotFoundException,
    RoleNotFoundException,
    PermissionNotFoundException,
    RoleAlreadyAssignedException,
    RoleNotAssignedException,
)

__all__ = [
    "get_user_roles",
    "get_user_permissions",
    "get_role_by_code",
    "get_all_roles",
    "assign_role_to_user",
    "remove_role_from_user",
    "get_permission_by_code",
    "get_all_permissions",
    "get_permissions_by_resource",
    "UUID",
    "RBACException",
    "UserNotFoundException",
    "RoleNotFoundException",
    "PermissionNotFoundException",
    "RoleAlreadyAssignedException",
    "RoleNotAssignedException",
]

