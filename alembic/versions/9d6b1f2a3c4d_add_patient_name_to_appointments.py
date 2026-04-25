"""add patient name snapshot to appointments

Revision ID: 9d6b1f2a3c4d
Revises: 5f25611a860f
Create Date: 2026-04-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9d6b1f2a3c4d"
down_revision: Union[str, Sequence[str], None] = "5f25611a860f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "appointments",
        sa.Column("patient_first_name", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "appointments",
        sa.Column("patient_last_name", sa.String(length=50), nullable=True),
    )

    op.execute(
        """
        UPDATE appointments
        SET patient_first_name = COALESCE(
                (SELECT applications.first_name
                 FROM applications
                 WHERE applications.id = appointments.application_id),
                users.first_name
            ),
            patient_last_name = COALESCE(
                (SELECT applications.last_name
                 FROM applications
                 WHERE applications.id = appointments.application_id),
                users.last_name
            )
        FROM users
        WHERE users.id = appointments.patient_id
        """
    )

    op.alter_column(
        "appointments",
        "patient_first_name",
        existing_type=sa.String(length=50),
        nullable=False,
    )
    op.alter_column(
        "appointments",
        "patient_last_name",
        existing_type=sa.String(length=50),
        nullable=False,
    )


def downgrade() -> None:
    op.drop_column("appointments", "patient_last_name")
    op.drop_column("appointments", "patient_first_name")
