"""add psychologist comment to appointments

Revision ID: e2f3a4b5c6d7
Revises: d4f0e5a6b7c8
Create Date: 2026-05-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e2f3a4b5c6d7"
down_revision: Union[str, Sequence[str], None] = "d4f0e5a6b7c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "appointments",
        "conclusion",
        existing_type=sa.String(length=2048),
        existing_nullable=True,
        comment="Комментарий пациенту",
    )
    op.add_column(
        "appointments",
        sa.Column(
            "psychologist_comment",
            sa.String(length=2048),
            nullable=True,
            comment="Комментарий психологам",
        ),
    )


def downgrade() -> None:
    op.drop_column("appointments", "psychologist_comment")
    op.alter_column(
        "appointments",
        "conclusion",
        existing_type=sa.String(length=2048),
        existing_nullable=True,
        comment="Заключение психолога",
    )
