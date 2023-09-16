from typing import TYPE_CHECKING
from pydantic import UUID4
from app.core.db.mixins.timestamp_mixin import TimestampMixin
from sqlalchemy import Float, Integer, ForeignKey, String, Text
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.models import Base, GUID

if TYPE_CHECKING:
    from app.models.community import Post


class AiCoaching(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    post_id: Mapped[Integer] = mapped_column(
        Integer, ForeignKey("post.id", ondelete="SET NULL"), nullable=False, index=True
    )
    user_id: Mapped[UUID4] = mapped_column(GUID, ForeignKey("user.id", ondelete="SET NULL"), nullable=False, index=True)

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
