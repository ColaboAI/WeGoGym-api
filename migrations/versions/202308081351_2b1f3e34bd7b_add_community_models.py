"""Add community models

Revision ID: 2b1f3e34bd7b
Revises: b14cf3d76b6e
Create Date: 2023-08-08 13:51:56.696851

"""
from alembic import op
import sqlalchemy as sa
import app.models.guid

# revision identifiers, used by Alembic.
revision = "2b1f3e34bd7b"
down_revision = "b14cf3d76b6e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "community",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("type", sa.Integer(), nullable=False, comment="1: 운동 2: 식단 3: 자유 4: 질문"),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=False),
        sa.Column("image", sa.String(length=1000), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_community")),
        sa.UniqueConstraint("name", name=op.f("uq_community_name")),
    )
    op.create_index(op.f("ix_community_id"), "community", ["id"], unique=False)
    op.create_table(
        "post",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("content", sa.String(length=1000), nullable=False),
        sa.Column("image", sa.String(length=1000), nullable=True),
        sa.Column("video", sa.String(length=1000), nullable=True),
        sa.Column("user_id", app.models.guid.GUID(), nullable=True),
        sa.Column("community_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["community_id"],
            ["community.id"],
            name=op.f("fk_post_community_id_community"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], name=op.f("fk_post_user_id_user")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_post")),
    )
    op.create_index(op.f("ix_post_id"), "post", ["id"], unique=False)
    op.create_table(
        "comment",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("is_ai_coach", sa.Integer(), nullable=False),
        sa.Column("content", sa.String(length=1000), nullable=False),
        sa.Column("user_id", app.models.guid.GUID(), nullable=True),
        sa.Column("post_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["post_id"], ["post.id"], name=op.f("fk_comment_post_id_post")),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], name=op.f("fk_comment_user_id_user")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_comment")),
    )
    op.create_index(op.f("ix_comment_id"), "comment", ["id"], unique=False)
    op.create_table(
        "post_like",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("is_like", sa.Boolean(), nullable=False),
        sa.Column("user_id", app.models.guid.GUID(), nullable=True),
        sa.Column("post_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["post_id"], ["post.id"], name=op.f("fk_post_like_post_id_post")),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], name=op.f("fk_post_like_user_id_user")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_post_like")),
        sa.UniqueConstraint("user_id", "post_id", name=op.f("uq_post_like_user_id")),
    )
    op.create_index(op.f("ix_post_like_id"), "post_like", ["id"], unique=False)
    op.create_table(
        "comment_like",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("is_like", sa.Integer(), nullable=False),
        sa.Column("user_id", app.models.guid.GUID(), nullable=True),
        sa.Column("comment_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["comment_id"],
            ["comment.id"],
            name=op.f("fk_comment_like_comment_id_comment"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], name=op.f("fk_comment_like_user_id_user")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_comment_like")),
        sa.UniqueConstraint("user_id", "comment_id", name=op.f("uq_comment_like_user_id")),
    )
    op.create_index(op.f("ix_comment_like_id"), "comment_like", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_comment_like_id"), table_name="comment_like")
    op.drop_table("comment_like")
    op.drop_index(op.f("ix_post_like_id"), table_name="post_like")
    op.drop_table("post_like")
    op.drop_index(op.f("ix_comment_id"), table_name="comment")
    op.drop_table("comment")
    op.drop_index(op.f("ix_post_id"), table_name="post")
    op.drop_table("post")
    op.drop_index(op.f("ix_community_id"), table_name="community")
    op.drop_table("community")
    # ### end Alembic commands ###
