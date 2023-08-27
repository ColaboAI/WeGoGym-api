"""Fix foreignkey options

Revision ID: 54e116a5e8d1
Revises: 3711c3442d81
Create Date: 2023-08-10 01:20:52.636685

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '54e116a5e8d1'
down_revision = '3711c3442d81'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('comment', 'user_id',
               existing_type=postgresql.UUID(),
               nullable=False)
    op.alter_column('comment', 'post_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.create_index(op.f('ix_comment_post_id'), 'comment', ['post_id'], unique=False)
    op.create_index(op.f('ix_comment_user_id'), 'comment', ['user_id'], unique=False)
    op.drop_constraint('fk_comment_user_id_user', 'comment', type_='foreignkey')
    op.drop_constraint('fk_comment_post_id_post', 'comment', type_='foreignkey')
    op.create_foreign_key(op.f('fk_comment_post_id_post'), 'comment', 'post', ['post_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(op.f('fk_comment_user_id_user'), 'comment', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.alter_column('comment_like', 'user_id',
               existing_type=postgresql.UUID(),
               nullable=False)
    op.alter_column('comment_like', 'comment_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.create_index(op.f('ix_comment_like_comment_id'), 'comment_like', ['comment_id'], unique=False)
    op.create_index(op.f('ix_comment_like_user_id'), 'comment_like', ['user_id'], unique=False)
    op.drop_constraint('fk_comment_like_user_id_user', 'comment_like', type_='foreignkey')
    op.drop_constraint('fk_comment_like_comment_id_comment', 'comment_like', type_='foreignkey')
    op.create_foreign_key(op.f('fk_comment_like_user_id_user'), 'comment_like', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(op.f('fk_comment_like_comment_id_comment'), 'comment_like', 'comment', ['comment_id'], ['id'], ondelete='CASCADE')
    op.alter_column('post', 'user_id',
               existing_type=postgresql.UUID(),
               nullable=False)
    op.alter_column('post', 'community_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.create_index(op.f('ix_post_community_id'), 'post', ['community_id'], unique=False)
    op.create_index(op.f('ix_post_user_id'), 'post', ['user_id'], unique=False)
    op.drop_constraint('fk_post_user_id_user', 'post', type_='foreignkey')
    op.create_foreign_key(op.f('fk_post_user_id_user'), 'post', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.alter_column('post_like', 'user_id',
               existing_type=postgresql.UUID(),
               nullable=False)
    op.alter_column('post_like', 'post_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.create_index(op.f('ix_post_like_post_id'), 'post_like', ['post_id'], unique=False)
    op.create_index(op.f('ix_post_like_user_id'), 'post_like', ['user_id'], unique=False)
    op.drop_constraint('fk_post_like_user_id_user', 'post_like', type_='foreignkey')
    op.drop_constraint('fk_post_like_post_id_post', 'post_like', type_='foreignkey')
    op.create_foreign_key(op.f('fk_post_like_user_id_user'), 'post_like', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(op.f('fk_post_like_post_id_post'), 'post_like', 'post', ['post_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_post_like_post_id_post'), 'post_like', type_='foreignkey')
    op.drop_constraint(op.f('fk_post_like_user_id_user'), 'post_like', type_='foreignkey')
    op.create_foreign_key('fk_post_like_post_id_post', 'post_like', 'post', ['post_id'], ['id'])
    op.create_foreign_key('fk_post_like_user_id_user', 'post_like', 'user', ['user_id'], ['id'])
    op.drop_index(op.f('ix_post_like_user_id'), table_name='post_like')
    op.drop_index(op.f('ix_post_like_post_id'), table_name='post_like')
    op.alter_column('post_like', 'post_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('post_like', 'user_id',
               existing_type=postgresql.UUID(),
               nullable=True)
    op.drop_constraint(op.f('fk_post_user_id_user'), 'post', type_='foreignkey')
    op.create_foreign_key('fk_post_user_id_user', 'post', 'user', ['user_id'], ['id'])
    op.drop_index(op.f('ix_post_user_id'), table_name='post')
    op.drop_index(op.f('ix_post_community_id'), table_name='post')
    op.alter_column('post', 'community_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('post', 'user_id',
               existing_type=postgresql.UUID(),
               nullable=True)
    op.drop_constraint(op.f('fk_comment_like_comment_id_comment'), 'comment_like', type_='foreignkey')
    op.drop_constraint(op.f('fk_comment_like_user_id_user'), 'comment_like', type_='foreignkey')
    op.create_foreign_key('fk_comment_like_comment_id_comment', 'comment_like', 'comment', ['comment_id'], ['id'])
    op.create_foreign_key('fk_comment_like_user_id_user', 'comment_like', 'user', ['user_id'], ['id'])
    op.drop_index(op.f('ix_comment_like_user_id'), table_name='comment_like')
    op.drop_index(op.f('ix_comment_like_comment_id'), table_name='comment_like')
    op.alter_column('comment_like', 'comment_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('comment_like', 'user_id',
               existing_type=postgresql.UUID(),
               nullable=True)
    op.drop_constraint(op.f('fk_comment_user_id_user'), 'comment', type_='foreignkey')
    op.drop_constraint(op.f('fk_comment_post_id_post'), 'comment', type_='foreignkey')
    op.create_foreign_key('fk_comment_post_id_post', 'comment', 'post', ['post_id'], ['id'])
    op.create_foreign_key('fk_comment_user_id_user', 'comment', 'user', ['user_id'], ['id'])
    op.drop_index(op.f('ix_comment_user_id'), table_name='comment')
    op.drop_index(op.f('ix_comment_post_id'), table_name='comment')
    op.alter_column('comment', 'post_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('comment', 'user_id',
               existing_type=postgresql.UUID(),
               nullable=True)
    # ### end Alembic commands ###