"""Combined migration: RBAC system, therapists refactoring, and datetime improvements

Revision ID: combined_rbac_improvements
Revises: d789ac864327
Create Date: 2025-10-27

This migration combines multiple changes:
1. Transforms old 'roles' table (user_id, role enum) to new structure (id, code, name, description)
2. Creates new RBAC system (permissions, roles, users_roles, roles_permissions)
3. Renames 'therapists' table to 'psychologists' and adds user_id (separate PK from users)
4. Renames 'therapist_id' to 'psychologist_id' in appointments table
5. Adds scheduled_time and comment to appointments
6. Converts datetime columns to timezone-aware (TIMESTAMP WITH TIME ZONE)
7. Seeds RBAC roles and permissions data
8. Assigns roles to existing users

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.dialects import postgresql
from datetime import datetime, timezone
import uuid


# revision identifiers, used by Alembic.
revision: str = 'combined_rbac_improvements'
down_revision: Union[str, Sequence[str], None] = 'd789ac864327'
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

users_table = table('users',
    column('id', postgresql.UUID)
)

psychologists_table = table('psychologists',
    column('id', postgresql.UUID),
    column('user_id', postgresql.UUID)
)

users_roles_table = table('users_roles',
    column('user_id', postgresql.UUID),
    column('role_id', postgresql.UUID),
    column('assigned_at', sa.DateTime)
)


# RBAC Data definitions
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
    
    # Psychologists permissions
    {"code": PermissionCode.PSYCHOLOGISTS_EDIT_OWN_PROFILE.name, "name": "Редактирование профиля психолога", "description": "Редактирование данных психолога", "resource": "psychologists"},
    {"code": PermissionCode.PSYCHOLOGISTS_MANAGE.name, "name": "Управление психологами", "description": "CRUD операции над психологами", "resource": "psychologists"},
    
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
            PermissionCode.PSYCHOLOGISTS_EDIT_OWN_PROFILE.name,
        ]
    },
    {
        "code": RoleCode.ADMIN.name,
        "name": "Администратор",
        "description": "Администратор системы",
        "permissions": [
            PermissionCode.APPOINTMENTS_VIEW_ALL.name,
            PermissionCode.APPOINTMENTS_EDIT_ALL.name,
            PermissionCode.APPOINTMENTS_DELETE_ALL.name,
            PermissionCode.REVIEWS_VIEW_ALL.name,
            PermissionCode.STATISTICS_VIEW.name,
            PermissionCode.PSYCHOLOGISTS_MANAGE.name,
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
    """Apply all combined changes."""
    conn = op.get_bind()
    
    # ========================================
    # STEP 1: Modify appointments table
    # ========================================
    # Add new columns (scheduled_time as nullable first, then we'll make it NOT NULL)
    op.add_column('appointments', sa.Column('scheduled_time', sa.DateTime(timezone=True), nullable=True, comment='Время назначенной встречи'))
    op.add_column('appointments', sa.Column('comment', sa.String(length=512), nullable=True, comment='Комментарий к записи'))
    
    # Fill scheduled_time with default value for existing rows (use current timestamp)
    conn.execute(sa.text("""
        UPDATE appointments 
        SET scheduled_time = CURRENT_TIMESTAMP 
        WHERE scheduled_time IS NULL
    """))
    
    # Now make scheduled_time NOT NULL
    op.alter_column('appointments', 'scheduled_time',
                    existing_type=sa.DateTime(timezone=True),
                    nullable=False)
    
    # Convert existing datetime columns to timezone-aware
    op.alter_column('appointments', 'remind_time',
               existing_type=sa.DateTime(),
               type_=sa.DateTime(timezone=True),
               comment='Время напоминания',
               existing_nullable=True)
    
    op.alter_column('appointments', 'last_change_time',
               existing_type=sa.DateTime(),
               type_=sa.DateTime(timezone=True),
               comment='Время последнего изменения',
               existing_nullable=False)
    
    op.alter_column('appointments', 'venue',
               existing_type=sa.VARCHAR(length=128),
               comment='Место проведения встречи',
               existing_nullable=False)
    
    # ========================================
    # STEP 2: Modify and rename therapists table to psychologists
    # ========================================
    # First, drop all FK constraints that reference therapists.id
    op.drop_constraint('appointments_therapist_id_fkey', 'appointments', type_='foreignkey')
    op.drop_constraint('therapists_id_fkey', 'therapists', type_='foreignkey')
    
    # Add user_id column as nullable first (for existing rows after downgrade)
    op.add_column('therapists', sa.Column('user_id', sa.UUID(), nullable=True))
    
    # Fill user_id with id value for existing rows (in old schema, id was the user_id)
    conn.execute(sa.text("UPDATE therapists SET user_id = id WHERE user_id IS NULL"))
    
    # Generate new UUIDs for id column (to separate psychologist id from user id)
    conn.execute(sa.text("UPDATE therapists SET id = gen_random_uuid()"))
    
    # Now make user_id NOT NULL and create indices
    op.alter_column('therapists', 'user_id',
                    existing_type=sa.UUID(),
                    nullable=False)
    
    # Drop indices if they exist (from previous rollback) and recreate them
    conn.execute(sa.text("DROP INDEX IF EXISTS ix_therapists_id"))
    conn.execute(sa.text("DROP INDEX IF EXISTS ix_therapists_user_id"))
    op.create_index(op.f('ix_therapists_id'), 'therapists', ['id'], unique=False)
    op.create_index(op.f('ix_therapists_user_id'), 'therapists', ['user_id'], unique=True)
    
    # Create new FK constraint for user_id
    op.create_foreign_key('therapists_user_id_fkey', 'therapists', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    
    # Rename therapists table to psychologists
    op.rename_table('therapists', 'psychologists')
    
    # Rename indices after table rename
    op.execute('ALTER INDEX ix_therapists_id RENAME TO ix_psychologists_id')
    op.execute('ALTER INDEX ix_therapists_user_id RENAME TO ix_psychologists_user_id')
    
    # Rename foreign key constraint name
    op.execute('ALTER TABLE psychologists RENAME CONSTRAINT therapists_user_id_fkey TO psychologists_user_id_fkey')
    
    # Update appointments to reference new psychologist ids
    # Update appointments.therapist_id to reference new psychologists.id (via user_id mapping)
    conn.execute(sa.text("""
        UPDATE appointments a
        SET therapist_id = p.id
        FROM psychologists p
        WHERE a.therapist_id = p.user_id
    """))
    
    # Rename the column
    op.alter_column('appointments', 'therapist_id',
                    new_column_name='psychologist_id',
                    existing_type=sa.UUID(),
                    existing_nullable=False)
    
    # Create new FK
    op.create_foreign_key('appointments_psychologist_id_fkey', 'appointments', 'psychologists', ['psychologist_id'], ['id'], ondelete='CASCADE')
    
    # ========================================
    # STEP 3: Transform old roles table to new structure
    # ========================================
    # Rename old roles table temporarily
    op.rename_table('roles', 'roles_old')
    
    # Drop old enum types if they exist (for re-running migrations)
    conn.execute(sa.text("DROP TYPE IF EXISTS rolecode CASCADE"))
    conn.execute(sa.text("DROP TYPE IF EXISTS permissioncode CASCADE"))
    
    # Create new roles table with new structure
    op.create_table('roles',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('code', sa.Enum('USER', 'PSYCHOLOGIST', 'ADMIN', 'CONTENT_MANAGER', name='rolecode'), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_code'), 'roles', ['code'], unique=True)
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)
    
    # ========================================
    # STEP 4: Create new RBAC tables
    # ========================================
    # Create permissions table
    op.create_table('permissions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('code', sa.Enum('APPOINTMENTS_CREATE_OWN', 'APPOINTMENTS_VIEW_OWN', 'APPOINTMENTS_CANCEL_OWN', 'APPOINTMENTS_CONFIRM_OWN', 'APPOINTMENTS_VIEW_PENDING', 'APPOINTMENTS_ACCEPT', 'APPOINTMENTS_RESCHEDULE', 'APPOINTMENTS_REJECT', 'APPOINTMENTS_VIEW_ALL', 'APPOINTMENTS_EDIT_ALL', 'APPOINTMENTS_DELETE_ALL', 'REVIEWS_CREATE_OWN', 'REVIEWS_VIEW_ALL', 'USERS_EDIT_OWN_PROFILE', 'PSYCHOLOGISTS_EDIT_OWN_PROFILE', 'PSYCHOLOGISTS_MANAGE', 'STATISTICS_VIEW', 'FAQ_EDIT', 'MATERIALS_CREATE', 'MATERIALS_EDIT', 'MATERIALS_DELETE', 'TESTS_CREATE', 'TESTS_EDIT', 'TESTS_DELETE', name='permissioncode'), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('resource', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_permissions_code'), 'permissions', ['code'], unique=True)
    op.create_index(op.f('ix_permissions_id'), 'permissions', ['id'], unique=False)
    op.create_index(op.f('ix_permissions_resource'), 'permissions', ['resource'], unique=False)
    
    # Create roles_permissions junction table
    op.create_table('roles_permissions',
        sa.Column('role_id', sa.UUID(), nullable=False),
        sa.Column('permission_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )
    
    # Create users_roles junction table
    op.create_table('users_roles',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('role_id', sa.UUID(), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )
    
    # ========================================
    # STEP 5: Seed RBAC data
    # ========================================
    # Insert permissions
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
    
    # Insert roles and their permissions
    role_ids = {}
    for role_data in ROLES:
        role_id = uuid.uuid4()
        role_ids[role_data['code']] = role_id
        
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
    
    # ========================================
    # STEP 6: Assign roles to existing users
    # ========================================
    # Get all users
    users_result = conn.execute(
        sa.text("SELECT id FROM users")
    ).fetchall()
    
    # Get all psychologist user_ids
    psychologists_result = conn.execute(
        sa.text("SELECT user_id FROM psychologists")
    ).fetchall()
    
    psychologist_user_ids = {row[0] for row in psychologists_result}
    
    # Assign 'user' role to all users
    user_role_id = role_ids[RoleCode.USER.name]
    psychologist_role_id = role_ids[RoleCode.PSYCHOLOGIST.name]
    
    for user_row in users_result:
        user_id = user_row[0]
        
        # Assign 'user' role
        conn.execute(
            users_roles_table.insert().values(
                user_id=user_id,
                role_id=user_role_id,
                assigned_at=datetime.now(timezone.utc)
            )
        )
    
    # Assign 'psychologist' role to psychologists
    for psychologist_user_id in psychologist_user_ids:
        conn.execute(
            users_roles_table.insert().values(
                user_id=psychologist_user_id,
                role_id=psychologist_role_id,
                assigned_at=datetime.now(timezone.utc)
            )
        )
    
    # ========================================
    # STEP 7: Drop old roles table
    # ========================================
    op.drop_table('roles_old')


def downgrade() -> None:
    """Revert all combined changes."""
    conn = op.get_bind()
    
    # Drop old enum type if it exists
    conn.execute(sa.text("DROP TYPE IF EXISTS userrole CASCADE"))
    
    # Recreate old roles table structure
    op.create_table('roles_old',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('role', sa.Enum('Therapist', 'Administrator', name='userrole'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'role')
    )
    
    # Drop RBAC tables (in reverse order)
    op.drop_table('users_roles')
    op.drop_table('roles_permissions')
    op.drop_index(op.f('ix_roles_id'), table_name='roles')
    op.drop_index(op.f('ix_roles_code'), table_name='roles')
    op.drop_table('roles')
    op.drop_index(op.f('ix_permissions_resource'), table_name='permissions')
    op.drop_index(op.f('ix_permissions_id'), table_name='permissions')
    op.drop_index(op.f('ix_permissions_code'), table_name='permissions')
    op.drop_table('permissions')
    
    # Rename roles_old back to roles
    op.rename_table('roles_old', 'roles')
    
    # Revert appointments foreign key changes (psychologist_id -> therapist_id)
    op.drop_constraint('appointments_psychologist_id_fkey', 'appointments', type_='foreignkey')
    
    # Revert psychologists table rename
    op.rename_table('psychologists', 'therapists')
    
    # Now update appointments to reference the new therapists table structure
    # First, update therapist_id in appointments to match the user_id from therapists
    conn.execute(sa.text("""
        UPDATE appointments a
        SET psychologist_id = t.user_id
        FROM therapists t
        WHERE a.psychologist_id = t.id
    """))
    
    # Rename the column
    op.alter_column('appointments', 'psychologist_id',
                    new_column_name='therapist_id',
                    existing_type=sa.UUID(),
                    existing_nullable=False)
    
    # Rename indices back after table rename
    op.execute('ALTER INDEX ix_psychologists_id RENAME TO ix_therapists_id')
    op.execute('ALTER INDEX ix_psychologists_user_id RENAME TO ix_therapists_user_id')
    
    # Rename foreign key constraint back
    op.execute('ALTER TABLE therapists RENAME CONSTRAINT psychologists_user_id_fkey TO therapists_user_id_fkey')
    
    # Migrate data: copy user_id to id (preserving the relationship)
    # First drop constraints and indices
    op.drop_constraint('therapists_user_id_fkey', 'therapists', type_='foreignkey')
    op.drop_constraint('therapists_pkey', 'therapists', type_='primary')
    op.drop_index(op.f('ix_therapists_id'), table_name='therapists')
    op.drop_index(op.f('ix_therapists_user_id'), table_name='therapists')
    
    # Update id to be equal to user_id
    conn.execute(sa.text("UPDATE therapists SET id = user_id"))
    
    # Drop user_id column
    op.drop_column('therapists', 'user_id')
    
    # Recreate constraints with id as FK to users
    op.create_foreign_key('therapists_id_fkey', 'therapists', 'users', ['id'], ['id'], ondelete='CASCADE')
    op.create_primary_key('therapists_pkey', 'therapists', ['id'])
    op.create_index(op.f('ix_therapists_id'), 'therapists', ['id'], unique=False)
    
    # Recreate appointments foreign key with old name
    op.create_foreign_key('appointments_therapist_id_fkey', 'appointments', 'therapists', ['therapist_id'], ['id'], ondelete='CASCADE')
    
    # Revert appointments changes
    op.alter_column('appointments', 'venue',
               existing_type=sa.VARCHAR(length=128),
               comment=None,
               existing_comment='Место проведения встречи',
               existing_nullable=False)
    
    op.alter_column('appointments', 'last_change_time',
               existing_type=sa.DateTime(timezone=True),
               type_=sa.DateTime(),
               comment=None,
               existing_comment='Время последнего изменения',
               existing_nullable=False)
    
    op.alter_column('appointments', 'remind_time',
               existing_type=sa.DateTime(timezone=True),
               type_=sa.DateTime(),
               comment=None,
               existing_comment='Время напоминания',
               existing_nullable=True)
    
    op.drop_column('appointments', 'comment')
    op.drop_column('appointments', 'scheduled_time')

