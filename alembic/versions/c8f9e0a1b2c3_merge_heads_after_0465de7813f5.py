"""merge heads after 0465de7813f5

Revision ID: c8f9e0a1b2c3
Revises: e2f3a4b5c6d7, 4ad174116c62
Create Date: 2026-05-09

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "c8f9e0a1b2c3"
down_revision: Union[str, Sequence[str], None] = ("e2f3a4b5c6d7", "4ad174116c62")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge parallel branches; schema changes live in parent revisions."""
    pass


def downgrade() -> None:
    """Merge points cannot be split automatically."""
    pass
