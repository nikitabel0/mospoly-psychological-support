"""fix_appointment_status_enum

Revision ID: 5f25611a860f
Revises: 50630bbac52f
Create Date: 2026-04-19 01:37:40.661271

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f25611a860f'
down_revision: Union[str, Sequence[str], None] = '50630bbac52f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Переименовываем старый тип, чтобы освободить имя
    op.execute("ALTER TYPE appointmentstatus RENAME TO appointmentstatus_old")

    # 2. Создаем новый правильный тип (только 3 значения в нижнем регистре)
    op.execute("CREATE TYPE appointmentstatus AS ENUM('awaiting', 'cancelled', 'done')")

    # 3. Меняем тип колонки в таблице. 
    # CASE нужен, чтобы база поняла, как перевести старые записи (с большой буквы) в новые.
    op.execute("""
        ALTER TABLE appointments 
        ALTER COLUMN status TYPE appointmentstatus 
        USING (
            CASE status::text
                WHEN 'Approved' THEN 'awaiting'
                WHEN 'Accepted' THEN 'awaiting'
                WHEN 'Cancelled' THEN 'cancelled'
                WHEN 'Done' THEN 'done'
                ELSE 'awaiting'
            END
        )::appointmentstatus
    """)

    # 4. Удаляем старый мусорный тип
    op.execute("DROP TYPE appointmentstatus_old")


def downgrade() -> None:
    # Возврат к старому типу, если вдруг придется откатывать эту миграцию
    op.execute("ALTER TYPE appointmentstatus RENAME TO appointmentstatus_new")
    op.execute("CREATE TYPE appointmentstatus AS ENUM('Approved', 'Accepted', 'Cancelled', 'Done')")
    op.execute("""
        ALTER TABLE appointments 
        ALTER COLUMN status TYPE appointmentstatus 
        USING (
            CASE status::text
                WHEN 'awaiting' THEN 'Accepted'
                WHEN 'cancelled' THEN 'Cancelled'
                WHEN 'done' THEN 'Done'
                ELSE 'Accepted'
            END
        )::appointmentstatus
    """)
    op.execute("DROP TYPE appointmentstatus_new")
