"""NewStatuses

Revision ID: 50630bbac52f
Revises: 62e8ab982071
Create Date: 2026-04-18 14:29:09.812923

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50630bbac52f'
down_revision: Union[str, Sequence[str], None] = '62e8ab982071'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Переименовываем старый тип
    op.execute("ALTER TYPE appointmentstatus RENAME TO appointmentstatus_old")

    # 2. Создаем новый тип ТОЛЬКО с тремя нужными статусами
    op.execute("CREATE TYPE appointmentstatus AS ENUM('awaiting', 'cancelled', 'done')")

    # 3. Меняем тип колонки. Если в базе были какие-то старые записи, 
    # жестко сбрасываем их статус на 'awaiting', чтобы избежать ошибок.
    op.execute(
        "ALTER TABLE appointments "
        "ALTER COLUMN status TYPE appointmentstatus "
        "USING 'awaiting'::appointmentstatus"
    )

    # 4. Удаляем старый тип с концами
    op.execute("DROP TYPE appointmentstatus_old")


def downgrade() -> None:
    # Возвращаем старый тип (на случай отката миграции)
    op.execute("ALTER TYPE appointmentstatus RENAME TO appointmentstatus_new")
    op.execute("CREATE TYPE appointmentstatus AS ENUM('Approved', 'Accepted', 'Cancelled', 'Done')")
    op.execute(
        "ALTER TABLE appointments "
        "ALTER COLUMN status TYPE appointmentstatus "
        "USING 'Accepted'::appointmentstatus"
    )
    op.execute("DROP TYPE appointmentstatus_new")