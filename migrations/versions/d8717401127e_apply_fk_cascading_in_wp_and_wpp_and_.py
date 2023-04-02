"""Apply fk cascading in wp and wpp and chat room

Revision ID: d8717401127e
Revises: 8ac29a2082ef
Create Date: 2023-04-03 01:01:19.577734

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd8717401127e'
down_revision = '8ac29a2082ef'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_chat_room_admin_user_id_user', 'chat_room', type_='foreignkey')
    op.create_foreign_key(op.f('fk_chat_room_admin_user_id_user'), 'chat_room', 'user', ['admin_user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('fk_workout_participant_workout_promise_id_workout_promise', 'workout_participant', type_='foreignkey')
    op.create_foreign_key(op.f('fk_workout_participant_workout_promise_id_workout_promise'), 'workout_participant', 'workout_promise', ['workout_promise_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('fk_workout_promise_admin_user_id_user', 'workout_promise', type_='foreignkey')
    op.create_foreign_key(op.f('fk_workout_promise_admin_user_id_user'), 'workout_promise', 'user', ['admin_user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_workout_promise_admin_user_id_user'), 'workout_promise', type_='foreignkey')
    op.create_foreign_key('fk_workout_promise_admin_user_id_user', 'workout_promise', 'user', ['admin_user_id'], ['id'], ondelete='SET NULL')
    op.drop_constraint(op.f('fk_workout_participant_workout_promise_id_workout_promise'), 'workout_participant', type_='foreignkey')
    op.create_foreign_key('fk_workout_participant_workout_promise_id_workout_promise', 'workout_participant', 'workout_promise', ['workout_promise_id'], ['id'], ondelete='SET NULL')
    op.drop_constraint(op.f('fk_chat_room_admin_user_id_user'), 'chat_room', type_='foreignkey')
    op.create_foreign_key('fk_chat_room_admin_user_id_user', 'chat_room', 'user', ['admin_user_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###
