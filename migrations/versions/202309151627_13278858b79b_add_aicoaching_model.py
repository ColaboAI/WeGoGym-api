"""Add AiCoaching model

Revision ID: 13278858b79b
Revises: 273be3d0ccde
Create Date: 2023-09-15 16:27:08.286733

"""
from alembic import op
import sqlalchemy as sa
import app.models.guid

# revision identifiers, used by Alembic.
revision = "13278858b79b"
down_revision = "273be3d0ccde"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "ai_coaching",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("user_id", app.models.guid.GUID(), nullable=False),
        sa.Column("response", sa.Text(), nullable=False),
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
            ["post_id"], ["post.id"], name=op.f("fk_ai_coaching_post_id_post"), ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], name=op.f("fk_ai_coaching_user_id_user"), ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ai_coaching")),
    )
    op.create_index(op.f("ix_ai_coaching_id"), "ai_coaching", ["id"], unique=False)
    op.create_index(op.f("ix_ai_coaching_post_id"), "ai_coaching", ["post_id"], unique=False)
    op.create_index(op.f("ix_ai_coaching_user_id"), "ai_coaching", ["user_id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_ai_coaching_user_id"), table_name="ai_coaching")
    op.drop_index(op.f("ix_ai_coaching_post_id"), table_name="ai_coaching")
    op.drop_index(op.f("ix_ai_coaching_id"), table_name="ai_coaching")
    op.drop_table("ai_coaching")
    # ### end Alembic commands ###
