"""Add timestampmixin

Revision ID: 6616a3c2ca62
Revises: 18db465dffe3
Create Date: 2023-02-01 16:06:35.753088

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "6616a3c2ca62"
down_revision = "18db465dffe3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "chat_room_member",
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
    )
    op.add_column(
        "chat_room_member",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
    )
    op.alter_column(
        "chat_room_member",
        "last_read_at",
        type=sa.DateTime(),
        existing_type=postgresql.TIMESTAMP(),
        server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
        nullable=False,
    )
    op.alter_column(
        "chat_room_member",
        "left_at",
        type=sa.DateTime(),
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
    )
    op.drop_column("chat_room_member", "joined_at")

    op.alter_column(
        "chat_room",
        "created_at",
        type=sa.DateTime(),
        existing_type=postgresql.TIMESTAMP(),
        server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
        nullable=False,
    )

    op.alter_column(
        "chat_room",
        "updated_at",
        type=sa.DateTime(),
        existing_type=postgresql.TIMESTAMP(),
        server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
        nullable=False,
    )

    op.add_column(
        "message",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
    )
    op.alter_column(
        "message",
        "created_at",
        type=sa.DateTime(),
        existing_type=postgresql.TIMESTAMP(),
        server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
        nullable=False,
    )

    op.add_column(
        "user",
        sa.Column(
            "is_superuser",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )
    op.add_column(
        "user",
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
    )
    op.add_column(
        "user",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
    )
    op.drop_column("user", "last_active_at")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "user",
        sa.Column("last_active_at", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.drop_column("user", "updated_at")
    op.drop_column("user", "created_at")
    op.drop_column("user", "is_superuser")
    op.drop_column("message", "updated_at")
    op.add_column(
        "chat_room_member",
        sa.Column("joined_at", postgresql.TIMESTAMP(), nullable=False),
    )
    op.alter_column(
        "chat_room_member",
        "last_read_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
    )
    op.alter_column(
        "chat_room_member",
        "left_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
    )
    op.alter_column(
        "chat_room",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
    )

    op.alter_column(
        "chat_room",
        "updated_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
    )

    op.drop_column("chat_room_member", "updated_at")
    op.drop_column("chat_room_member", "created_at")
    # ### end Alembic commands ###
