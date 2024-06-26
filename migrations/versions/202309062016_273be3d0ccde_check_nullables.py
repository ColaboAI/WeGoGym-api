"""Check nullables

Revision ID: 273be3d0ccde
Revises: 54e116a5e8d1
Create Date: 2023-09-06 20:16:18.010320

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "273be3d0ccde"
down_revision = "54e116a5e8d1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("fk_chat_room_admin_user_id_user", "chat_room", type_="foreignkey")
    op.create_foreign_key(
        op.f("fk_chat_room_admin_user_id_user"), "chat_room", "user", ["admin_user_id"], ["id"], ondelete="SET NULL"
    )
    op.alter_column("gym_info", "is_custom_gym", existing_type=sa.BOOLEAN(), nullable=False)
    op.alter_column("notification_workout", "sender_id", existing_type=sa.UUID(), nullable=False)
    op.alter_column("notification_workout", "recipient_id", existing_type=sa.UUID(), nullable=False)
    op.alter_column("workout_participant", "status", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column("workout_participant", "user_id", existing_type=sa.UUID(), nullable=False)
    op.alter_column("workout_participant", "workout_promise_id", existing_type=sa.UUID(), nullable=False)
    op.alter_column("workout_promise", "is_private", existing_type=sa.BOOLEAN(), nullable=False)
    op.alter_column(
        "workout_promise",
        "promise_time",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=False,
        existing_server_default=sa.text("timezone('utc'::text, CURRENT_TIMESTAMP)"),
    )
    op.alter_column("workout_promise", "admin_user_id", existing_type=sa.UUID(), nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("workout_promise", "admin_user_id", existing_type=sa.UUID(), nullable=True)
    op.alter_column(
        "workout_promise",
        "promise_time",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=True,
        existing_server_default=sa.text("timezone('utc'::text, CURRENT_TIMESTAMP)"),
    )
    op.alter_column("workout_promise", "is_private", existing_type=sa.BOOLEAN(), nullable=True)
    op.alter_column("workout_participant", "workout_promise_id", existing_type=sa.UUID(), nullable=True)
    op.alter_column("workout_participant", "user_id", existing_type=sa.UUID(), nullable=True)
    op.alter_column("workout_participant", "status", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column("notification_workout", "recipient_id", existing_type=sa.UUID(), nullable=True)
    op.alter_column("notification_workout", "sender_id", existing_type=sa.UUID(), nullable=True)
    op.alter_column("gym_info", "is_custom_gym", existing_type=sa.BOOLEAN(), nullable=True)
    op.drop_constraint(op.f("fk_chat_room_admin_user_id_user"), "chat_room", type_="foreignkey")
    op.create_foreign_key(
        "fk_chat_room_admin_user_id_user", "chat_room", "user", ["admin_user_id"], ["id"], ondelete="CASCADE"
    )
    # ### end Alembic commands ###
