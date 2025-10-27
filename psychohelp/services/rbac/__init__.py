"""
RBAC (Role-Based Access Control) services
"""

from .permissions import (
    user_has_permission,
    get_user_permissions,
    get_user_roles,
    require_permission,
)

__all__ = [
    "user_has_permission",
    "get_user_permissions",
    "get_user_roles",
    "require_permission",
]

