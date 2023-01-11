"""Remove Prototyping Model

Revision ID: a9d2cd01a72c
Revises: b10d8bb4a8cb
Create Date: 2023-01-11 14:39:46.741083

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a9d2cd01a72c'
down_revision = 'b10d8bb4a8cb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_prototyping_id', table_name='prototyping')
    op.drop_table('prototyping')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('prototyping',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('email', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='prototyping_pkey')
    )
    op.create_index('ix_prototyping_id', 'prototyping', ['id'], unique=False)
    # ### end Alembic commands ###