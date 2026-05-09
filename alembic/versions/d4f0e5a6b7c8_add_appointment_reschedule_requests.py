"""add appointment reschedule requests

Revision ID: d4f0e5a6b7c8
Revises: 0465de7813f5
Create Date: 2026-05-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4f0e5a6b7c8"
down_revision: Union[str, Sequence[str], None] = "0465de7813f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "appointment_reschedule_requests",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("appointment_id", sa.UUID(), nullable=False),
        sa.Column("requested_by_user_id", sa.UUID(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "confirmed",
                "rejected",
                name="appointmentreschedulestatus",
            ),
            nullable=False,
        ),
        sa.Column("old_scheduled_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("old_remind_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("old_venue", sa.String(length=128), nullable=False),
        sa.Column("old_comment", sa.String(length=512), nullable=True),
        sa.Column("requested_scheduled_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("requested_remind_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("requested_venue", sa.String(length=128), nullable=True),
        sa.Column("requested_comment", sa.String(length=512), nullable=True),
        sa.Column("rejection_comment", sa.String(length=512), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["appointment_id"], ["appointments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_appointment_reschedule_requests_id"),
        "appointment_reschedule_requests",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_appointment_reschedule_requests_appointment_id"),
        "appointment_reschedule_requests",
        ["appointment_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_appointment_reschedule_requests_requested_by_user_id"),
        "appointment_reschedule_requests",
        ["requested_by_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_appointment_reschedule_requests_status"),
        "appointment_reschedule_requests",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_appointment_reschedule_requests_one_pending_per_appointment",
        "appointment_reschedule_requests",
        ["appointment_id"],
        unique=True,
        postgresql_where=sa.text("status = 'pending'"),
    )


def downgrade() -> None:
    op.drop_index(
        "ix_appointment_reschedule_requests_one_pending_per_appointment",
        table_name="appointment_reschedule_requests",
    )
    op.drop_index(
        op.f("ix_appointment_reschedule_requests_status"),
        table_name="appointment_reschedule_requests",
    )
    op.drop_index(
        op.f("ix_appointment_reschedule_requests_requested_by_user_id"),
        table_name="appointment_reschedule_requests",
    )
    op.drop_index(
        op.f("ix_appointment_reschedule_requests_appointment_id"),
        table_name="appointment_reschedule_requests",
    )
    op.drop_index(
        op.f("ix_appointment_reschedule_requests_id"),
        table_name="appointment_reschedule_requests",
    )
    op.drop_table("appointment_reschedule_requests")
    sa.Enum(name="appointmentreschedulestatus").drop(op.get_bind(), checkfirst=True)
