"""merge migration heads

Revision ID: 0cb1de8797bf
Revises: 065e485b58c3, 76ea597063ce, f3a4b5c6d7e8
Create Date: 2026-10-05 14:11:36.350687

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0cb1de8797bf'
down_revision: Union[str, Sequence[str], None] = ('065e485b58c3', '76ea597063ce', 'f3a4b5c6d7e8')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
