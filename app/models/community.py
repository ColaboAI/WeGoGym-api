from re import U
from app.core.db.mixins.timestamp_mixin import TimestampMixin
from app.models import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
    Boolean,
    TEXT,
)
from sqlalchemy.orm import relationship, query_expression, Mapped
from app.models.guid import GUID

from app.models.user import User


class Community(TimestampMixin, Base):
    __tablename__ = "community"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(
        Integer, nullable=False, server_default="1", comment="1: 운동 2: 식단 3: 자유 4: 질문"
    )
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(1000), nullable=False)
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="community")


class Post(TimestampMixin, Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    content = Column(TEXT, nullable=False)
    available = Column(Boolean, nullable=False, server_default="1")
    image = Column(TEXT)
    video = Column(TEXT)
    user_id = Column(
        GUID, ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False
    )
    community_id = Column(
        Integer,
        ForeignKey("community.id"),
        index=True,
        nullable=False,
    )
    user: Mapped[User] = relationship("User", back_populates="posts")
    community: Mapped[Community] = relationship("Community", back_populates="posts")
    post_likes: Mapped[list["PostLike"]] = relationship(
        "PostLike", back_populates="post"
    )
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post")

    like_cnt: Mapped[int] = query_expression()
    comment_cnt: Mapped[int] = query_expression()


class PostLike(TimestampMixin, Base):
    __tablename__ = "post_like"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    is_liked = Column(Integer, nullable=False)
    user_id = Column(
        GUID, ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False
    )
    post_id = Column(
        Integer, ForeignKey("post.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user: Mapped[User] = relationship(
        "User", back_populates="post_likes", uselist=False
    )
    post: Mapped[Post] = relationship("Post", back_populates="post_likes")
    __table_args__ = (UniqueConstraint("user_id", "post_id"),)


class Comment(TimestampMixin, Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    is_ai_coach = Column(Integer, nullable=False, server_default="0")
    available = Column(Boolean, nullable=False, server_default="1")
    content = Column(TEXT, nullable=False)
    user_id = Column(
        GUID, ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False
    )
    post_id = Column(
        Integer, ForeignKey("post.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user: Mapped[User] = relationship("User", back_populates="comments", uselist=False)
    post: Mapped[Post] = relationship("Post", back_populates="comments", uselist=False)
    comment_likes: Mapped[list["CommentLike"]] = relationship(
        "CommentLike", back_populates="comment"
    )

    like_cnt: Mapped[int] = query_expression()


class CommentLike(TimestampMixin, Base):
    __tablename__ = "comment_like"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    is_liked = Column(Integer, nullable=False)
    user_id = Column(
        GUID, ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False
    )
    comment_id = Column(
        Integer,
        ForeignKey("comment.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    user: Mapped[User] = relationship("User", back_populates="comment_likes")
    comment: Mapped[Comment] = relationship("Comment", back_populates="comment_likes")
    __table_args__ = (UniqueConstraint("user_id", "comment_id"),)
