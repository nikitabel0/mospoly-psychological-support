"""seed rbac roles and permissions data

Revision ID: 772da19cfdce
Revises: 320096c5bd22
Create Date: 2025-10-26

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision: str = '772da19cfdce'
down_revision: Union[str, Sequence[str], None] = '320096c5bd22'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Import constants
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from psychohelp.constants.rbac import PermissionCode, RoleCode


# Define tables for data operations
permissions_table = table('permissions',
    column('id', postgresql.UUID),
    column('code', sa.String),
    column('name', sa.String),
    column('description', sa.String),
    column('resource', sa.String)
)

roles_table = table('roles',
    column('id', postgresql.UUID),
    column('code', sa.String),
    column('name', sa.String),
    column('description', sa.String)
)

roles_permissions_table = table('roles_permissions',
    column('role_id', postgresql.UUID),
    column('permission_id', postgresql.UUID)
)


# Data definitions - используем .name для native enum!
PERMISSIONS = [
    # Appointments permissions
    {"code": PermissionCode.APPOINTMENTS_CREATE_OWN.name, "name": "Создание своих записей", "description": "Возможность создавать записи на консультацию", "resource": "appointments"},
    {"code": PermissionCode.APPOINTMENTS_VIEW_OWN.name, "name": "Просмотр своих записей", "description": "Просмотр своих текущих и прошлых записей", "resource": "appointments"},
    {"code": PermissionCode.APPOINTMENTS_CANCEL_OWN.name, "name": "Отмена своих записей", "description": "Возможность отменить свою запись", "resource": "appointments"},
    {"code": PermissionCode.APPOINTMENTS_CONFIRM_OWN.name, "name": "Подтверждение своих записей", "description": "Возможность подтвердить свою запись", "resource": "appointments"},
    {"code": PermissionCode.APPOINTMENTS_VIEW_PENDING.name, "name": "Просмотр записей на рассмотрении", "description": "Просмотр записей со статусом 'На рассмотрении'", "resource": "appointments"},
    {"code": PermissionCode.APPOINTMENTS_ACCEPT.name, "name": "Принятие записей", "description": "Возможность принять запись на консультацию", "resource": "appointments"},
    {"code": PermissionCode.APPOINTMENTS_RESCHEDULE.name, "name": "Перенос записей", "description": "Возможность перенести запись", "resource": "appointments"},
    {"code": PermissionCode.APPOINTMENTS_REJECT.name, "name": "Отклонение записей", "description": "Возможность отклонить запись", "resource": "appointments"},
    {"code": PermissionCode.APPOINTMENTS_VIEW_ALL.name, "name": "Просмотр всех записей", "description": "Просмотр всех записей в системе", "resource": "appointments"},
    {"code": PermissionCode.APPOINTMENTS_EDIT_ALL.name, "name": "Редактирование всех записей", "description": "Редактирование любых записей", "resource": "appointments"},
    {"code": PermissionCode.APPOINTMENTS_DELETE_ALL.name, "name": "Удаление всех записей", "description": "Удаление любых записей", "resource": "appointments"},
    
    # Reviews permissions
    {"code": PermissionCode.REVIEWS_CREATE_OWN.name, "name": "Создание отзывов", "description": "Возможность оставить отзыв после консультации", "resource": "reviews"},
    {"code": PermissionCode.REVIEWS_VIEW_ALL.name, "name": "Просмотр всех отзывов", "description": "Просмотр всех отзывов пользователей", "resource": "reviews"},
    
    # Users permissions
    {"code": PermissionCode.USERS_EDIT_OWN_PROFILE.name, "name": "Редактирование своего профиля", "description": "Редактирование личных данных", "resource": "users"},
    
    # Therapists permissions
    {"code": PermissionCode.THERAPISTS_EDIT_OWN_PROFILE.name, "name": "Редактирование профиля психолога", "description": "Редактирование данных психолога", "resource": "therapists"},
    {"code": PermissionCode.THERAPISTS_MANAGE.name, "name": "Управление психологами", "description": "CRUD операции над психологами", "resource": "therapists"},
    
    # Statistics permissions
    {"code": PermissionCode.STATISTICS_VIEW.name, "name": "Просмотр статистики", "description": "Просмотр статистики системы", "resource": "statistics"},
    
    # FAQ permissions
    {"code": PermissionCode.FAQ_EDIT.name, "name": "Редактирование FAQ", "description": "Редактирование раздела FAQ", "resource": "faq"},
    
    # Materials permissions
    {"code": PermissionCode.MATERIALS_CREATE.name, "name": "Создание материалов", "description": "Добавление полезных материалов", "resource": "materials"},
    {"code": PermissionCode.MATERIALS_EDIT.name, "name": "Редактирование материалов", "description": "Редактирование материалов", "resource": "materials"},
    {"code": PermissionCode.MATERIALS_DELETE.name, "name": "Удаление материалов", "description": "Удаление материалов", "resource": "materials"},
    
    # Tests permissions
    {"code": PermissionCode.TESTS_CREATE.name, "name": "Создание тестов", "description": "Добавление тестов/анкет", "resource": "tests"},
    {"code": PermissionCode.TESTS_EDIT.name, "name": "Редактирование тестов", "description": "Редактирование тестов/анкет", "resource": "tests"},
    {"code": PermissionCode.TESTS_DELETE.name, "name": "Удаление тестов", "description": "Удаление тестов/анкет", "resource": "tests"},
]

ROLES = [
    {
        "code": RoleCode.USER.name,
        "name": "Пользователь",
        "description": "Студент или преподаватель - обычный пользователь системы",
        "permissions": [
            PermissionCode.APPOINTMENTS_CREATE_OWN.name,
            PermissionCode.APPOINTMENTS_VIEW_OWN.name,
            PermissionCode.APPOINTMENTS_CANCEL_OWN.name,
            PermissionCode.APPOINTMENTS_CONFIRM_OWN.name,
            PermissionCode.REVIEWS_CREATE_OWN.name,
            PermissionCode.USERS_EDIT_OWN_PROFILE.name,
        ]
    },
    {
        "code": RoleCode.PSYCHOLOGIST.name,
        "name": "Психолог",
        "description": "Психолог, проводящий консультации",
        "permissions": [
            PermissionCode.APPOINTMENTS_VIEW_PENDING.name,
            PermissionCode.APPOINTMENTS_ACCEPT.name,
            PermissionCode.APPOINTMENTS_RESCHEDULE.name,
            PermissionCode.APPOINTMENTS_REJECT.name,
            PermissionCode.USERS_EDIT_OWN_PROFILE.name,
            PermissionCode.THERAPISTS_EDIT_OWN_PROFILE.name,
        ]
    },
    {
        "code": RoleCode.HEAD_OF_PSYCHOLOGISTS.name,
        "name": "Руководитель психологов",
        "description": "Руководитель психологической службы",
        "permissions": [
            PermissionCode.APPOINTMENTS_VIEW_ALL.name,
            PermissionCode.APPOINTMENTS_EDIT_ALL.name,
            PermissionCode.APPOINTMENTS_DELETE_ALL.name,
            PermissionCode.REVIEWS_VIEW_ALL.name,
            PermissionCode.STATISTICS_VIEW.name,
            PermissionCode.THERAPISTS_MANAGE.name,
        ]
    },
    {
        "code": RoleCode.CONTENT_MANAGER.name,
        "name": "Контент-менеджер",
        "description": "Управление контентом сайта",
        "permissions": [
            PermissionCode.FAQ_EDIT.name,
            PermissionCode.MATERIALS_CREATE.name,
            PermissionCode.MATERIALS_EDIT.name,
            PermissionCode.MATERIALS_DELETE.name,
            PermissionCode.TESTS_CREATE.name,
            PermissionCode.TESTS_EDIT.name,
            PermissionCode.TESTS_DELETE.name,
        ]
    },
]


def upgrade() -> None:
    """Seed initial RBAC data."""
    conn = op.get_bind()
    
    # 1. Insert permissions
    permission_ids = {}
    for perm in PERMISSIONS:
        perm_id = uuid.uuid4()
        permission_ids[perm['code']] = perm_id
        
        conn.execute(
            permissions_table.insert().values(
                id=perm_id,
                code=perm['code'],
                name=perm['name'],
                description=perm['description'],
                resource=perm['resource']
            )
        )
    
    # 2. Insert roles and their permissions
    for role_data in ROLES:
        role_id = uuid.uuid4()
        
        # Insert role
        conn.execute(
            roles_table.insert().values(
                id=role_id,
                code=role_data['code'],
                name=role_data['name'],
                description=role_data['description']
            )
        )
        
        # Link role with permissions
        for perm_code in role_data['permissions']:
            conn.execute(
                roles_permissions_table.insert().values(
                    role_id=role_id,
                    permission_id=permission_ids[perm_code]
                )
            )


def downgrade() -> None:
    """Remove seeded RBAC data."""
    conn = op.get_bind()
    
    # Delete in reverse order (respecting foreign keys)
    conn.execute(roles_permissions_table.delete())
    conn.execute(roles_table.delete())
    conn.execute(permissions_table.delete())
