"""rename instagram user id

Revision ID: 555e79e4e675
Revises: 85638eaaac33
Create Date: 2026-07-21 14:24:09.278268

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '555e79e4e675'
down_revision: Union[str, Sequence[str], None] = '85638eaaac33'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        op.f('mutual_followers_user_id_fkey'),
        'mutual_followers',
        type_='foreignkey'
    )

    op.alter_column(
        'instagram_users',
        'id',
        new_column_name='insta_user_id'
    )

    op.create_foreign_key(
        'mutual_followers_user_id_fkey',
        'mutual_followers',
        'instagram_users',
        ['user_id'],
        ['insta_user_id']
    )


def downgrade() -> None:
    op.drop_constraint(
        'mutual_followers_user_id_fkey',
        'mutual_followers',
        type_='foreignkey'
    )

    op.alter_column(
        'instagram_users',
        'insta_user_id',
        new_column_name='id'
    )

    op.create_foreign_key(
        'mutual_followers_user_id_fkey',
        'mutual_followers',
        'instagram_users',
        ['user_id'],
        ['id']
    )
