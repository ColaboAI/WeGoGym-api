"""
SQL Alchemy models declaration.

Note, imported by alembic migrations logic, see `alembic/env.py`
"""


from datetime import datetime
from typing import TYPE_CHECKING
from pydantic import UUID4
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    text,
)
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.db.mixins.timestamp_mixin import TimestampMixin

from app.models import Base
from app.models.chat import ChatRoom, Message
from app.models.guid import GUID
import uuid
from app.models.workout_promise import WorkoutParticipant


if TYPE_CHECKING:
    from app.models import GymInfo, Post, PostLike, Comment, CommentLike


user_block_list = Table(
    "user_block_list",
    Base.metadata,
    Column(
        "user_id",
        GUID,
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
    Column(
        "blocked_user_id",
        GUID,
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
)


class User(TimestampMixin, Base):  # type: ignore
    id: Mapped[UUID4] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    # TODO: username check
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    phone_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, server_default=expression.false(), nullable=False)
    profile_pic: Mapped[str] = mapped_column(String(255), nullable=True)
    bio: Mapped[str] = mapped_column(String(100), nullable=True)
    # TODO: age to be calculated from birthdate

    age: Mapped[str] = mapped_column(String(50), server_default="20220701", nullable=False)
    weight: Mapped[int] = mapped_column(Integer, server_default=text("0"), nullable=False)
    height: Mapped[int] = mapped_column(Integer, server_default=text("0"), nullable=False)
    gender: Mapped[str] = mapped_column(String(50), server_default="other", nullable=False)
    workout_per_week: Mapped[int] = mapped_column(Integer, server_default=text("0"), nullable=False)
    workout_level: Mapped[str | None] = mapped_column(String(100), nullable=True)
    workout_goal: Mapped[str | None] = mapped_column(String(255), nullable=True)
    workout_time_per_day: Mapped[str | None] = mapped_column(String(100), nullable=True)
    workout_time_period: Mapped[str | None] = mapped_column(String(50), nullable=True)
    workout_style: Mapped[str | None] = mapped_column(String(255), nullable=True)
    workout_routine: Mapped[str | None] = mapped_column(String(255), nullable=True)
    workout_partner_gender: Mapped[str | None] = mapped_column(String(50), nullable=True)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    district: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fcm_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # TODO: last_active_at should be updated when user is active (init app)
    # remove fcm_token when user is inactive with 2 months
    last_active_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Child relationship with GymInfo ("many" to one)
    gym_info_id: Mapped[UUID4] = mapped_column(GUID, ForeignKey("gym_info.id", ondelete="SET NULL"))
    gym_info: Mapped["GymInfo"] = relationship("GymInfo", back_populates="users")

    # Parent relationship with ChatRoomMember (Many to "One")
    chat_room_members: Mapped[list[ChatRoom]] = relationship(
        "ChatRoomMember",
        back_populates="user",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )
    # Parent relationship with Message (Many to "One")
    messages: Mapped[list[Message]] = relationship(
        "Message",
        back_populates="user",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )

    # Parent relationship with WorkoutParticipant (Many to "One")
    workout_participants: Mapped[list[WorkoutParticipant]] = relationship(
        "WorkoutParticipant",
        back_populates="user",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )

    # Parent relationship with WorkoutPromise (One to Many) (Admin)
    # What promises this user has made or is Admin of
    admin_workout_promises: Mapped[list[WorkoutParticipant]] = relationship(
        "WorkoutPromise",
        back_populates="admin_user",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )

    admin_chat_rooms: Mapped[list[ChatRoom]] = relationship(
        "ChatRoom",
        back_populates="admin_user",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )

    # 앱 전체에서 차단 여부
    blocked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        server_default=expression.false(),
    )
    blocked_users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="blocked_by_users_list",
        secondary=user_block_list,
        primaryjoin=id == user_block_list.c.user_id,
        secondaryjoin=id == user_block_list.c.blocked_user_id,
    )

    blocked_by_users_list: Mapped[list["User"]] = relationship(
        "User",
        back_populates="blocked_users",
        secondary=user_block_list,
        primaryjoin=id == user_block_list.c.blocked_user_id,
        secondaryjoin=id == user_block_list.c.user_id,
    )

    posts: Mapped[list["Post"]] = relationship(
        "Post",
        back_populates="user",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )

    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="user",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )

    post_likes: Mapped[list["PostLike"]] = relationship(
        "PostLike",
        back_populates="user",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )

    comment_likes: Mapped[list["CommentLike"]] = relationship(
        "CommentLike",
        back_populates="user",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )
