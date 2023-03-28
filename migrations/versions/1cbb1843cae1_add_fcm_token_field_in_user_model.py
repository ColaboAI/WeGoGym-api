"""Add fcm_token field in user model

Revision ID: 1cbb1843cae1
Revises: 7daeea4f4b5c
Create Date: 2023-03-21 15:49:56.220073

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1cbb1843cae1'
down_revision = '7daeea4f4b5c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('fcm_token', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'fcm_token')
    # ### end Alembic commands ###