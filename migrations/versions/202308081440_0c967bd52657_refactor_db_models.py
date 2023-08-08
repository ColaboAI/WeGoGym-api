"""Refactor db models

Revision ID: 0c967bd52657
Revises: 2b1f3e34bd7b
Create Date: 2023-08-08 14:40:29.949011

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c967bd52657'
down_revision = '2b1f3e34bd7b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('available', sa.Boolean(), server_default='1', nullable=False))
    op.alter_column('comment', 'content',
               existing_type=sa.VARCHAR(length=1000),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.drop_column('community', 'image')
    op.add_column('post', sa.Column('available', sa.Boolean(), server_default='1', nullable=False))
    op.alter_column('post', 'content',
               existing_type=sa.VARCHAR(length=1000),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.alter_column('post', 'image',
               existing_type=sa.VARCHAR(length=1000),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('post', 'video',
               existing_type=sa.VARCHAR(length=1000),
               type_=sa.TEXT(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('post', 'video',
               existing_type=sa.TEXT(),
               type_=sa.VARCHAR(length=1000),
               existing_nullable=True)
    op.alter_column('post', 'image',
               existing_type=sa.TEXT(),
               type_=sa.VARCHAR(length=1000),
               existing_nullable=True)
    op.alter_column('post', 'content',
               existing_type=sa.TEXT(),
               type_=sa.VARCHAR(length=1000),
               existing_nullable=False)
    op.drop_column('post', 'available')
    op.add_column('community', sa.Column('image', sa.VARCHAR(length=1000), autoincrement=False, nullable=True))
    op.alter_column('comment', 'content',
               existing_type=sa.TEXT(),
               type_=sa.VARCHAR(length=1000),
               existing_nullable=False)
    op.drop_column('comment', 'available')
    # ### end Alembic commands ###
