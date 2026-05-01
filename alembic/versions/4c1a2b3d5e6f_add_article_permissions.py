"""add article permissions

Revision ID: 4c1a2b3d5e6f
Revises: 32f8a463f0b5
Create Date: 2026-05-01 00:00:00.000000

"""
from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


revision: str = "4c1a2b3d5e6f"
down_revision: Union[str, Sequence[str], None] = "32f8a463f0b5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ARTICLE_PERMISSIONS = (
    ("ARTICLES_CREATE", "Создание статей", "Возможность создавать статьи"),
    ("ARTICLES_EDIT", "Редактирование статей", "Возможность редактировать статьи"),
    ("ARTICLES_DELETE", "Удаление статей", "Возможность удалять статьи"),
)
PERMISSION_CODES_SQL = ", ".join(
    f"CAST('{code}' AS permissioncode)" for code, _name, _description in ARTICLE_PERMISSIONS
)


def upgrade() -> None:
    conn = op.get_bind()

    with op.get_context().autocommit_block():
        for code, _name, _description in ARTICLE_PERMISSIONS:
            op.execute(f"ALTER TYPE permissioncode ADD VALUE IF NOT EXISTS '{code}'")

    for code, name, description in ARTICLE_PERMISSIONS:
        conn.execute(
            sa.text(
                """
                INSERT INTO permissions (id, code, name, description, resource)
                VALUES (
                    CAST(:id AS uuid),
                    CAST(:code AS permissioncode),
                    :name,
                    :description,
                    'articles'
                )
                ON CONFLICT (code) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    resource = EXCLUDED.resource
                """
            ),
            {
                "id": str(uuid4()),
                "code": code,
                "name": name,
                "description": description,
            },
        )

    conn.execute(
        sa.text(
            f"""
            INSERT INTO roles_permissions (role_id, permission_id)
            SELECT roles.id, permissions.id
            FROM roles
            CROSS JOIN permissions
            WHERE roles.code = CAST('ADMIN' AS rolecode)
              AND permissions.code IN ({PERMISSION_CODES_SQL})
            ON CONFLICT DO NOTHING
            """
        )
    )


def downgrade() -> None:
    conn = op.get_bind()

    conn.execute(
        sa.text(
            f"""
            DELETE FROM roles_permissions
            WHERE permission_id IN (
                SELECT id
                FROM permissions
                WHERE code IN ({PERMISSION_CODES_SQL})
            )
            """
        )
    )
    conn.execute(
        sa.text(
            f"""
            DELETE FROM permissions
            WHERE code IN ({PERMISSION_CODES_SQL})
            """
        )
    )
