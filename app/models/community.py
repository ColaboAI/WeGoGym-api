from pydantic import UUID4
from app.ai.models import AiCoaching
from app.core.db.mixins.timestamp_mixin import TimestampMixin
from app.models import Base
from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
    Boolean,
    TEXT,
)
from sqlalchemy.orm import relationship, query_expression, Mapped, mapped_column
from app.models.guid import GUID

from app.models.user import User


class Community(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    type: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1", comment="1: 운동 2: 식단 3: 자유 4: 질문")
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="community")


class Post(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    summary: Mapped[str] = mapped_column(String(200), nullable=True, comment="Ai Summary")
    content: Mapped[str] = mapped_column(TEXT, nullable=False)
    available: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="1")
    image: Mapped[str] = mapped_column(TEXT, nullable=True)
    video: Mapped[str] = mapped_column(TEXT, nullable=True)
    user_id: Mapped[UUID4] = mapped_column(GUID, ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)
    community_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("community.id"),
        index=True,
        nullable=False,
    )
    user: Mapped[User] = relationship("User", back_populates="posts")
    community: Mapped[Community] = relationship("Community", back_populates="posts")
    post_likes: Mapped[list["PostLike"]] = relationship("PostLike", back_populates="post")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post")
    ai_coaching: Mapped[list["AiCoaching"]] = relationship("AiCoaching", back_populates="post")
    like_cnt: Mapped[int] = query_expression()
    comment_cnt: Mapped[int] = query_expression()

    is_liked: Mapped[int] = query_expression()


class PostLike(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    is_liked: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[UUID4] = mapped_column(GUID, ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)
    post_id: Mapped[UUID4] = mapped_column(
        Integer, ForeignKey("post.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user: Mapped[User] = relationship("User", back_populates="post_likes", uselist=False)
    post: Mapped[Post] = relationship("Post", back_populates="post_likes")
    __table_args__ = (UniqueConstraint("user_id", "post_id"),)


class Comment(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    is_ai_coach: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    available: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="1")
    content: Mapped[str] = mapped_column(TEXT, nullable=False)
    user_id: Mapped[UUID4] = mapped_column(GUID, ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("post.id", ondelete="CASCADE"), index=True, nullable=False)
    user: Mapped[User] = relationship("User", back_populates="comments", uselist=False)
    post: Mapped[Post] = relationship("Post", back_populates="comments", uselist=False)
    comment_likes: Mapped[list["CommentLike"]] = relationship("CommentLike", back_populates="comment")

    like_cnt: Mapped[int] = query_expression()
    is_liked: Mapped[int] = query_expression()


class CommentLike(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    is_liked: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[UUID4] = mapped_column(GUID, ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)
    comment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("comment.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    user: Mapped[User] = relationship("User", back_populates="comment_likes")
    comment: Mapped[Comment] = relationship("Comment", back_populates="comment_likes")
    __table_args__ = (UniqueConstraint("user_id", "comment_id"),)
