from typing import TYPE_CHECKING
from pydantic import UUID4
from app.core.db.mixins.timestamp_mixin import TimestampMixin
from sqlalchemy import Float, Integer, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship, mapped_column, Mapped, query_expression
from app.models import Base, GUID

if TYPE_CHECKING:
    from app.models.community import Post, User


class AiCoaching(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    post_id: Mapped[Integer] = mapped_column(
        Integer, ForeignKey("post.id", ondelete="SET NULL"), nullable=True, index=True
    )
    user_id: Mapped[UUID4] = mapped_column(GUID, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True)

    response: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="number of tokens in prompt", server_default="0"
    )
    completion_tokens: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="number of tokens in response", server_default="0"
    )
    cost: Mapped[float] = mapped_column(Float, nullable=False, comment="cost in USD", server_default="0.0")
    model_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="model used to generate response", server_default="gpt-3.5-turbo"
    )

    post: Mapped["Post"] = relationship("Post", back_populates="ai_coaching")

    ai_coaching_likes: Mapped["AiCoachingLike"] = relationship("AiCoachingLike", back_populates="ai_coaching")

    is_liked: Mapped[int] = query_expression()
    like_cnt: Mapped[int] = query_expression()


class AiCoachingLike(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    is_liked: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[UUID4] = mapped_column(GUID, ForeignKey("user.id", ondelete="SET NULL"), index=True, nullable=False)
    ai_coaching_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("ai_coaching.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    user: Mapped["User"] = relationship("User", back_populates="ai_coaching_likes")
    ai_coaching: Mapped[AiCoaching] = relationship("AiCoaching", back_populates="ai_coaching_likes")
    __table_args__ = (UniqueConstraint("user_id", "ai_coaching_id"),)
