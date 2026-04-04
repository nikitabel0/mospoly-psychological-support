"""applications workflow, audit log, appointment link

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-04-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_STATUS_MAP = (
    ("новая", "new"),
    ("в обработке", "in_progress"),
    ("завершена", "completed"),
    ("отклонена", "rejected"),
)


def upgrade() -> None:
    op.add_column(
        "applications",
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "applications",
        sa.Column("psychologist_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column("applications", sa.Column("meeting_type", sa.String(length=20), nullable=True))
    op.add_column(
        "applications",
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column("applications", sa.Column("location_address", sa.Text(), nullable=True))
    op.add_column("applications", sa.Column("meeting_url", sa.String(length=512), nullable=True))
    op.add_column(
        "applications",
        sa.Column("processing_started_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "applications",
        sa.Column("confirmation_requested_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "applications",
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "applications",
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "applications",
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "applications",
        sa.Column("expired_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column("applications", sa.Column("reject_reason", sa.Text(), nullable=True))
    op.add_column("applications", sa.Column("cancel_reason", sa.Text(), nullable=True))
    op.add_column("applications", sa.Column("cancel_initiator", sa.String(length=20), nullable=True))
    op.add_column("applications", sa.Column("internal_comment", sa.Text(), nullable=True))
    op.add_column(
        "applications",
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )

    op.create_foreign_key(
        "applications_assigned_to_fkey",
        "applications",
        "users",
        ["assigned_to"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "applications_psychologist_id_fkey",
        "applications",
        "psychologists",
        ["psychologist_id"],
        ["id"],
        ondelete="SET NULL",
    )

    for old, new in _STATUS_MAP:
        op.execute(
            sa.text("UPDATE applications SET status = :new WHERE status = :old").bindparams(
                new=new, old=old
            )
        )

    op.alter_column("applications", "preferred_campus", existing_type=sa.String(length=128), nullable=True)
    op.alter_column(
        "applications",
        "status",
        existing_type=sa.String(length=50),
        server_default=sa.text("'new'"),
        nullable=False,
    )

    op.create_index(op.f("ix_applications_status"), "applications", ["status"], unique=False)
    op.create_index(op.f("ix_applications_assigned_to"), "applications", ["assigned_to"], unique=False)

    op.add_column(
        "appointments",
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index(op.f("ix_appointments_application_id"), "appointments", ["application_id"], unique=False)
    op.create_foreign_key(
        "appointments_application_id_fkey",
        "appointments",
        "applications",
        ["application_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "application_audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("previous_status", sa.String(length=50), nullable=True),
        sa.Column("new_status", sa.String(length=50), nullable=False),
        sa.Column("actor_type", sa.String(length=20), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["application_id"],
            ["applications.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_application_audit_logs_application_id"),
        "application_audit_logs",
        ["application_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_application_audit_logs_application_id"), table_name="application_audit_logs")
    op.drop_table("application_audit_logs")

    op.drop_constraint("appointments_application_id_fkey", "appointments", type_="foreignkey")
    op.drop_index(op.f("ix_appointments_application_id"), table_name="appointments")
    op.drop_column("appointments", "application_id")

    op.drop_index(op.f("ix_applications_assigned_to"), table_name="applications")
    op.drop_index(op.f("ix_applications_status"), table_name="applications")

    op.alter_column(
        "applications",
        "status",
        existing_type=sa.String(length=50),
        server_default=sa.text("'новая'"),
        nullable=False,
    )
    for old, new in _STATUS_MAP:
        op.execute(
            sa.text("UPDATE applications SET status = :old WHERE status = :new").bindparams(
                old=old, new=new
            )
        )

    op.alter_column("applications", "preferred_campus", existing_type=sa.String(length=128), nullable=False)

    op.drop_constraint("applications_psychologist_id_fkey", "applications", type_="foreignkey")
    op.drop_constraint("applications_assigned_to_fkey", "applications", type_="foreignkey")

    op.drop_column("applications", "version")
    op.drop_column("applications", "internal_comment")
    op.drop_column("applications", "cancel_initiator")
    op.drop_column("applications", "cancel_reason")
    op.drop_column("applications", "reject_reason")
    op.drop_column("applications", "expired_at")
    op.drop_column("applications", "cancelled_at")
    op.drop_column("applications", "rejected_at")
    op.drop_column("applications", "completed_at")
    op.drop_column("applications", "confirmation_requested_at")
    op.drop_column("applications", "processing_started_at")
    op.drop_column("applications", "meeting_url")
    op.drop_column("applications", "location_address")
    op.drop_column("applications", "scheduled_at")
    op.drop_column("applications", "meeting_type")
    op.drop_column("applications", "psychologist_id")
    op.drop_column("applications", "assigned_to")
