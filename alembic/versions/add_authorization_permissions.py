"""add authorization permissions

Revision ID: add_authorization_permissions
Revises: 23020d3e0038
Create Date: 2025-11-23

This migration adds new permissions for authorization and role management:
- USERS_VIEW_ANY: View any user profile
- USERS_MANAGE: Manage users
- ROLES_ASSIGN: Assign roles to users
- ROLES_REMOVE: Remove roles from users
- ROLES_VIEW_ALL: View all roles
- PSYCHOLOGISTS_VIEW: View psychologists

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision: str = 'add_authorization_permissions'
down_revision: Union[str, Sequence[str], None] = '23020d3e0038'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Define tables for data operations
permissions_table = table('permissions',
    column('id', postgresql.UUID),
    column('code', sa.String),
    column('name', sa.String),
    column('description', sa.String),
    column('resource', sa.String)
)

roles_permissions_table = table('roles_permissions',
    column('role_id', postgresql.UUID),
    column('permission_id', postgresql.UUID)
)

roles_table = table('roles',
    column('id', postgresql.UUID),
    column('code', sa.String)
)


# New permissions to add
NEW_PERMISSIONS = [
    {
        "code": "USERS_VIEW_ANY",
        "name": "Просмотр профилей пользователей",
        "description": "Возможность просматривать профили других пользователей",
        "resource": "users"
    },
    {
        "code": "USERS_MANAGE",
        "name": "Управление пользователями",
        "description": "CRUD операции над пользователями",
        "resource": "users"
    },
    {
        "code": "ROLES_ASSIGN",
        "name": "Назначение ролей",
        "description": "Возможность назначать роли пользователям",
        "resource": "roles"
    },
    {
        "code": "ROLES_REMOVE",
        "name": "Удаление ролей",
        "description": "Возможность удалять роли у пользователей",
        "resource": "roles"
    },
    {
        "code": "ROLES_VIEW_ALL",
        "name": "Просмотр всех ролей",
        "description": "Просмотр всех ролей в системе",
        "resource": "roles"
    },
    {
        "code": "PSYCHOLOGISTS_VIEW",
        "name": "Просмотр психологов",
        "description": "Возможность просматривать список психологов",
        "resource": "psychologists"
    }
]


def upgrade() -> None:
    """Add new permissions and assign them to appropriate roles."""
    conn = op.get_bind()
    
    # First, update the PermissionCode enum to include new values
    # Note: In PostgreSQL, we need to add new enum values
    conn.execute(sa.text("ALTER TYPE permissioncode ADD VALUE IF NOT EXISTS 'USERS_VIEW_ANY'"))
    conn.execute(sa.text("ALTER TYPE permissioncode ADD VALUE IF NOT EXISTS 'USERS_MANAGE'"))
    conn.execute(sa.text("ALTER TYPE permissioncode ADD VALUE IF NOT EXISTS 'ROLES_ASSIGN'"))
    conn.execute(sa.text("ALTER TYPE permissioncode ADD VALUE IF NOT EXISTS 'ROLES_REMOVE'"))
    conn.execute(sa.text("ALTER TYPE permissioncode ADD VALUE IF NOT EXISTS 'ROLES_VIEW_ALL'"))
    conn.execute(sa.text("ALTER TYPE permissioncode ADD VALUE IF NOT EXISTS 'PSYCHOLOGISTS_VIEW'"))
    
    # Insert new permissions
    permission_ids = {}
    for perm in NEW_PERMISSIONS:
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
    
    # Get role IDs
    admin_role = conn.execute(
        sa.text("SELECT id FROM roles WHERE code = 'ADMIN'")
    ).fetchone()
    
    user_role = conn.execute(
        sa.text("SELECT id FROM roles WHERE code = 'USER'")
    ).fetchone()
    
    if admin_role:
        admin_role_id = admin_role[0]
        
        # Assign all new permissions to ADMIN role
        for perm_code in ['USERS_VIEW_ANY', 'USERS_MANAGE', 'ROLES_ASSIGN', 'ROLES_REMOVE', 'ROLES_VIEW_ALL', 'PSYCHOLOGISTS_VIEW']:
            conn.execute(
                roles_permissions_table.insert().values(
                    role_id=admin_role_id,
                    permission_id=permission_ids[perm_code]
                )
            )
    
    # Assign PSYCHOLOGISTS_VIEW to USER role (so users can view psychologists)
    if user_role:
        user_role_id = user_role[0]
        conn.execute(
            roles_permissions_table.insert().values(
                role_id=user_role_id,
                permission_id=permission_ids['PSYCHOLOGISTS_VIEW']
            )
        )


def downgrade() -> None:
    """Remove new permissions."""
    conn = op.get_bind()
    
    # Delete permissions (cascade will handle roles_permissions)
    for perm in NEW_PERMISSIONS:
        conn.execute(
            sa.text(f"DELETE FROM permissions WHERE code = '{perm['code']}'")
        )
    
    # Note: PostgreSQL doesn't support removing enum values easily,
    # so we leave them in the enum type. They won't cause issues.

