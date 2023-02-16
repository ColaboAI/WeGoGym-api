"""Add gym_address column

Revision ID: 3d011bb64820
Revises: c89fef1f823f
Create Date: 2023-02-16 13:06:15.148450

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d011bb64820'
down_revision = 'c89fef1f823f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('gym_address', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'gym_address')
    # ### end Alembic commands ###
