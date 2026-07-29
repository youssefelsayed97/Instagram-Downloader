"""updated 7/21 / 302

Revision ID: 3b77f45a1114
Revises: 555e79e4e675
Create Date: 2026-07-21 15:02:17.719691

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b77f45a1114'
down_revision: Union[str, Sequence[str], None] = '555e79e4e675'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # 1) remove foreign key dependency first
    op.drop_constraint(
        "mutual_followers_user_id_fkey",
        "mutual_followers",
        type_="foreignkey"
    )

    # 2) add new id column
    op.add_column(
        "instagram_users",
        sa.Column("id", sa.Integer(), nullable=True)
    )

    # 3) create sequence
    op.execute("""
        CREATE SEQUENCE IF NOT EXISTS instagram_users_id_seq;
    """)

    # 4) fill old rows
    op.execute("""
        UPDATE instagram_users
        SET id = nextval('instagram_users_id_seq');
    """)

    # 5) make id not null
    op.alter_column(
        "instagram_users",
        "id",
        nullable=False
    )

    # 6) drop old primary key
    op.drop_constraint(
        "instagram_users_pkey",
        "instagram_users",
        type_="primary"
    )

    # 7) create new primary key
    op.create_primary_key(
        "pk_instagram_users",
        "instagram_users",
        ["id"]
    )

    # 8) make insta_user_id unique
    op.create_unique_constraint(
        "uq_instagram_users_insta_user_id",
        "instagram_users",
        ["insta_user_id"]
    )

    # 9) recreate foreign key using insta_user_id
    op.create_foreign_key(
        "mutual_followers_user_id_fkey",
        "mutual_followers",
        "instagram_users",
        ["user_id"],
        ["insta_user_id"]
    )