"""fix appointments datetime columns timezone

Revision ID: 848d0c33edfc
Revises: 4476813c6b2d
Create Date: 2025-10-27 07:39:29.739123

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '848d0c33edfc'
down_revision: Union[str, Sequence[str], None] = '4476813c6b2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('appointments', 'scheduled_time',
                    existing_type=sa.TIMESTAMP(),
                    type_=sa.TIMESTAMP(timezone=True),
                    existing_nullable=False,
                    existing_comment='Время назначенной встречи')
    
    op.alter_column('appointments', 'remind_time',
                    existing_type=sa.TIMESTAMP(),
                    type_=sa.TIMESTAMP(timezone=True),
                    existing_nullable=True,
                    existing_comment='Время напоминания')
    
    op.alter_column('appointments', 'last_change_time',
                    existing_type=sa.TIMESTAMP(),
                    type_=sa.TIMESTAMP(timezone=True),
                    existing_nullable=False,
                    existing_comment='Время последнего изменения')


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('appointments', 'last_change_time',
                    existing_type=sa.TIMESTAMP(timezone=True),
                    type_=sa.TIMESTAMP(),
                    existing_nullable=False,
                    existing_comment='Время последнего изменения')
    
    op.alter_column('appointments', 'remind_time',
                    existing_type=sa.TIMESTAMP(timezone=True),
                    type_=sa.TIMESTAMP(),
                    existing_nullable=True,
                    existing_comment='Время напоминания')
    
    op.alter_column('appointments', 'scheduled_time',
                    existing_type=sa.TIMESTAMP(timezone=True),
                    type_=sa.TIMESTAMP(),
                    existing_nullable=False,
                    existing_comment='Время назначенной встречи')
