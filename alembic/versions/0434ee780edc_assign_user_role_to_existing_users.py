"""assign user role to existing users

Revision ID: 0434ee780edc
Revises: 772da19cfdce
Create Date: 2025-10-26

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.dialects import postgresql
from datetime import datetime, timezone


# revision identifiers, used by Alembic.
revision: str = '0434ee780edc'
down_revision: Union[str, Sequence[str], None] = '772da19cfdce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Import constants
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from psychohelp.constants.rbac import RoleCode


# Define tables
users_table = table('users',
    column('id', postgresql.UUID)
)

roles_table = table('roles',
    column('id', postgresql.UUID),
    column('code', sa.String)
)

therapists_table = table('therapists',
    column('id', postgresql.UUID),
    column('user_id', postgresql.UUID)
)

users_roles_table = table('users_roles',
    column('user_id', postgresql.UUID),
    column('role_id', postgresql.UUID),
    column('assigned_at', sa.DateTime)
)


def upgrade() -> None:
    """Assign 'user' role to all existing users and 'psychologist' to therapists."""
    conn = op.get_bind()
    
    # Get user role ID (используем .name для native enum!)
    user_role_result = conn.execute(
        sa.text("SELECT id FROM roles WHERE code = :code"),
        {"code": RoleCode.USER.name}
    ).fetchone()
    
    if not user_role_result:
        raise Exception(f"Role '{RoleCode.USER.name}' not found. Run seed migration first.")
    
    user_role_id = user_role_result[0]
    
    # Get psychologist role ID
    psychologist_role_result = conn.execute(
        sa.text("SELECT id FROM roles WHERE code = :code"),
        {"code": RoleCode.PSYCHOLOGIST.name}
    ).fetchone()
    
    if not psychologist_role_result:
        raise Exception(f"Role '{RoleCode.PSYCHOLOGIST.name}' not found. Run seed migration first.")
    
    psychologist_role_id = psychologist_role_result[0]
    
    # Get all users
    users_result = conn.execute(
        sa.text("SELECT id FROM users")
    ).fetchall()
    
    # Get all therapist user_ids
    therapists_result = conn.execute(
        sa.text("SELECT user_id FROM therapists")
    ).fetchall()
    
    therapist_user_ids = {row[0] for row in therapists_result}
    
    # Assign 'user' role to all users
    for user_row in users_result:
        user_id = user_row[0]
        
        # Check if user already has the 'user' role
        existing = conn.execute(
            sa.text("SELECT 1 FROM users_roles WHERE user_id = :user_id AND role_id = :role_id"),
            {"user_id": user_id, "role_id": user_role_id}
        ).fetchone()
        
        if not existing:
            conn.execute(
                users_roles_table.insert().values(
                    user_id=user_id,
                    role_id=user_role_id,
                    assigned_at=datetime.now(timezone.utc)
                )
            )
    
    # Assign 'psychologist' role to therapists
    for therapist_user_id in therapist_user_ids:
        # Check if therapist already has the 'psychologist' role
        existing = conn.execute(
            sa.text("SELECT 1 FROM users_roles WHERE user_id = :user_id AND role_id = :role_id"),
            {"user_id": therapist_user_id, "role_id": psychologist_role_id}
        ).fetchone()
        
        if not existing:
            conn.execute(
                users_roles_table.insert().values(
                    user_id=therapist_user_id,
                    role_id=psychologist_role_id,
                    assigned_at=datetime.now(timezone.utc)
                )
            )


def downgrade() -> None:
    """Remove role assignments for existing users."""
    conn = op.get_bind()
    
    # This migration is idempotent, so downgrade just removes all user-role assignments
    # that were created for existing users
    conn.execute(
        sa.text("DELETE FROM users_roles")
    )
