"""fix age column in user model

Revision ID: 5fd651c7cc19
Revises: d8717401127e
Create Date: 2023-04-07 18:42:51.212017

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5fd651c7cc19"
down_revision = "d8717401127e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "user",
        "age",
        existing_type=sa.INTEGER(),
        type_=sa.String(length=50),
        existing_nullable=False,
        server_default=sa.text("20220701"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user", "age")
    op.add_column(
        "user",
        sa.Column(
            "age",
            sa.INTEGER(),
            server_default=sa.text("0"),
            autoincrement=False,
            nullable=False,
        ),
    )
    # ### end Alembic commands ###