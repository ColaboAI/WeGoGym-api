"""Remove created by in Chat model

Revision ID: 201a1ccbbf2c
Revises: cdf2108ed38d
Create Date: 2023-04-01 22:00:08.585130

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '201a1ccbbf2c'
down_revision = 'cdf2108ed38d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_chat_room_admin_user_id'), 'chat_room', ['admin_user_id'], unique=False)
    op.drop_column('chat_room', 'created_by')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chat_room', sa.Column('created_by', postgresql.UUID(), autoincrement=False, nullable=False))
    op.drop_index(op.f('ix_chat_room_admin_user_id'), table_name='chat_room')
    # ### end Alembic commands ###
