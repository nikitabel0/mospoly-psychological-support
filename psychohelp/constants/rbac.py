"""
Enumы для RBAC системы
"""

from enum import Enum


class PermissionCode(str, Enum):
    """Коды прав доступа в системе"""
    
    # Appointments permissions
    APPOINTMENTS_CREATE_OWN = "appointments.create_own"
    APPOINTMENTS_VIEW_OWN = "appointments.view_own"
    APPOINTMENTS_CANCEL_OWN = "appointments.cancel_own"
    APPOINTMENTS_CONFIRM_OWN = "appointments.confirm_own"
    APPOINTMENTS_VIEW_PENDING = "appointments.view_pending"
    APPOINTMENTS_ACCEPT = "appointments.accept"
    APPOINTMENTS_RESCHEDULE = "appointments.reschedule"
    APPOINTMENTS_REJECT = "appointments.reject"
    APPOINTMENTS_VIEW_ALL = "appointments.view_all"
    APPOINTMENTS_EDIT_ALL = "appointments.edit_all"
    APPOINTMENTS_DELETE_ALL = "appointments.delete_all"
    
    # Reviews permissions
    REVIEWS_CREATE_OWN = "reviews.create_own"
    REVIEWS_VIEW_ALL = "reviews.view_all"
    
    # Users permissions
    USERS_EDIT_OWN_PROFILE = "users.edit_own_profile"
    
    # Therapists permissions
    THERAPISTS_EDIT_OWN_PROFILE = "therapists.edit_own_profile"
    THERAPISTS_MANAGE = "therapists.manage"
    
    # Statistics permissions
    STATISTICS_VIEW = "statistics.view"
    
    # FAQ permissions
    FAQ_EDIT = "faq.edit"
    
    # Materials permissions
    MATERIALS_CREATE = "materials.create"
    MATERIALS_EDIT = "materials.edit"
    MATERIALS_DELETE = "materials.delete"
    
    # Tests permissions
    TESTS_CREATE = "tests.create"
    TESTS_EDIT = "tests.edit"
    TESTS_DELETE = "tests.delete"


class RoleCode(str, Enum):
    """Коды ролей в системе"""
    
    USER = "user"
    PSYCHOLOGIST = "psychologist"
    HEAD_OF_PSYCHOLOGISTS = "head_of_psychologists"
    CONTENT_MANAGER = "content_manager"

