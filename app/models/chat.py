from datetime import datetime
from typing import TYPE_CHECKING
from pydantic import UUID4
from sqlalchemy import Boolean, String, ForeignKey, DateTime, true
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.db.mixins.timestamp_mixin import TimestampMixin
from app.models import Base
import uuid
from app.models.guid import GUID
from app.utils.generics import utcnow

if TYPE_CHECKING:
    # if the target of the relationship is in another module
    # that cannot normally be imported at runtime
    from . import User, WorkoutParticipant, WorkoutPromise


class ChatRoomMember(TimestampMixin, Base):
    __mapper_args__ = {"eager_defaults": True}
    id: Mapped[UUID4] = mapped_column(GUID, primary_key=True, index=True, default=uuid.uuid4)

    user_id: Mapped[UUID4] = mapped_column(GUID, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    chat_room_id: Mapped[UUID4] = mapped_column(
        GUID, ForeignKey("chat_room.id", ondelete="CASCADE"), nullable=False, index=True
    )
    left_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=utcnow(), nullable=True, default=None
    )
    last_read_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=utcnow(), nullable=False)
    last_read_message_id: Mapped[UUID4 | None] = mapped_column(GUID, nullable=True, default=None)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    chat_room: Mapped["ChatRoom"] = relationship("ChatRoom", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="chat_room_members")

    # 1:1 relationship with workout_participant
    workout_participant: Mapped["WorkoutParticipant"] = relationship(
        "WorkoutParticipant",
        back_populates="chat_room_member",
        cascade="save-update, merge, delete",
        passive_deletes=True,
        uselist=False,
    )


# TODO: delete Created by ?
class ChatRoom(TimestampMixin, Base):
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[UUID4] = mapped_column(GUID, primary_key=True, index=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=True)
    description: Mapped[str] = mapped_column(String(200), nullable=True)
    is_private: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, server_default=true())
    admin_user_id: Mapped[UUID4] = mapped_column(
        GUID, ForeignKey("user.id", ondelete="SET NULL"), index=True, nullable=True
    )
    admin_user: Mapped["User"] = relationship("User", back_populates="admin_chat_rooms")
    is_group_chat: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, server_default=true())

    members: Mapped[list[ChatRoomMember]] = relationship(
        "ChatRoomMember",
        back_populates="chat_room",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )

    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="chat_room",
        cascade="save-update, merge, delete",
        passive_deletes=True,
        order_by="Message.created_at.desc()",
    )

    # 1:1 relationship with workout_promise (deactivate collection)
    workout_promise: Mapped["WorkoutPromise"] = relationship(
        "WorkoutPromise",
        back_populates="chat_room",
        cascade="save-update, merge, delete",
        passive_deletes=True,
        uselist=False,
    )


# 유저 삭제 및 채팅방 삭제 시, text는 삭제되지 않음.
class Message(TimestampMixin, Base):
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[UUID4] = mapped_column(GUID, primary_key=True, index=True, default=uuid.uuid4)

    user: Mapped["User"] = relationship("User", back_populates="messages")
    user_id: Mapped[UUID4] = mapped_column(GUID, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)

    chat_room: Mapped[ChatRoom] = relationship("ChatRoom", back_populates="messages")
    chat_room_id: Mapped[UUID4] = mapped_column(GUID, ForeignKey("chat_room.id", ondelete="SET NULL"), nullable=True)

    text: Mapped[str] = mapped_column(String(300), nullable=True)
    media_url: Mapped[str] = mapped_column(String(256), nullable=True)
