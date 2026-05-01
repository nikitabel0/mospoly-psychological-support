"""create news table

Revision ID: 32f8a463f0b5
Revises: f1a2b3c4d5e6
Create Date: 2026-04-27 20:50:49.396406

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '32f8a463f0b5'
down_revision: Union[str, Sequence[str], None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # News only: application_audit_logs, application timestamps, and appointments.conclusion
    # are handled by revision 62e8ab982071 (earlier in the chain).
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if 'news' not in inspector.get_table_names():
        op.create_table('news',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False, comment='Заголовок новости'),
        sa.Column('text', sa.Text(), nullable=False, comment='Текст новости'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Дата и время создания'),
        sa.PrimaryKeyConstraint('id')
        )
    inspector = sa.inspect(bind)
    ix_news = op.f('ix_news_id')
    existing_ix = {i['name'] for i in inspector.get_indexes('news')} if 'news' in inspector.get_table_names() else set()
    if ix_news not in existing_ix:
        op.create_index(ix_news, 'news', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_news_id'), table_name='news')
    op.drop_table('news')
    # ### end Alembic commands ###
