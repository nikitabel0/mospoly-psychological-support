from enum import Enum


class PermissionCode(str, Enum):
    
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
    USERS_VIEW_ANY = "users.view_any"
    USERS_MANAGE = "users.manage"
    
    # Roles permissions
    ROLES_ASSIGN = "roles.assign"
    ROLES_REMOVE = "roles.remove"
    ROLES_VIEW_ALL = "roles.view_all"
    
    # Psychologists permissions
    PSYCHOLOGISTS_EDIT_OWN_PROFILE = "psychologists.edit_own_profile"
    PSYCHOLOGISTS_VIEW = "psychologists.view"
    PSYCHOLOGISTS_MANAGE = "psychologists.manage"
    
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
    USER = "user"
    PSYCHOLOGIST = "psychologist"
    ADMIN = "admin"
    CONTENT_MANAGER = "content_manager"

