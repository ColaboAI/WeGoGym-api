from typing import TYPE_CHECKING
from sqlalchemy import Boolean, Column, String, ForeignKey, DateTime, true
from sqlalchemy.orm import relationship
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
    __tablename__ = "chat_room_member"
    __mapper_args__ = {"eager_defaults": True}

    id = Column(GUID, primary_key=True, index=True, default=uuid.uuid4)

    chat_room: "ChatRoom" = relationship("ChatRoom", back_populates="members")
    chat_room_id = Column(
        GUID, ForeignKey("chat_room.id", ondelete="CASCADE"), nullable=False
    )

    left_at = Column(DateTime(timezone=True), server_default=utcnow(), nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    last_read_message_id = Column(GUID, nullable=True)
    last_read_at = Column(
        DateTime(timezone=True), server_default=utcnow(), nullable=False
    )

    user: "User" = relationship("User", back_populates="chat_room_members")
    user_id = Column(GUID, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    # 1:1 relationship with workout_participant
    workout_participant: "WorkoutParticipant" = relationship(
        "WorkoutParticipant",
        back_populates="chat_room_member",
        cascade="save-update, merge, delete",
        passive_deletes=True,
        uselist=False,
    )


class ChatRoom(TimestampMixin, Base):
    __tablename__ = "chat_room"
    __mapper_args__ = {"eager_defaults": True}

    id = Column(GUID, primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(String(200), nullable=False)
    created_by = Column(GUID, nullable=False, default=uuid.uuid4)
    is_private = Column(Boolean, default=True, nullable=False, server_default=true())
    admin_user_id = Column(GUID, ForeignKey("user.id", ondelete="SET NULL"))

    members: list[ChatRoomMember] = relationship(
        "ChatRoomMember",
        back_populates="chat_room",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )

    messages: list["Message"] = relationship(
        "Message",
        back_populates="chat_room",
        cascade="save-update, merge, delete",
        passive_deletes=True,
        order_by="Message.created_at.desc()",
    )

    # 1:1 relationship with workout_promise (deactivate collection)
    workout_promise: list["WorkoutPromise"] = relationship(
        "WorkoutPromise",
        back_populates="chat_room",
        cascade="save-update, merge, delete",
        passive_deletes=True,
        uselist=False,
    )


# 유저 삭제 및 채팅방 삭제 시, text는 삭제되지 않음.
class Message(TimestampMixin, Base):
    __tablename__ = "message"
    __mapper_args__ = {"eager_defaults": True}

    id = Column(GUID, primary_key=True, index=True, default=uuid.uuid4)

    user: "User" = relationship("User", back_populates="messages")
    user_id = Column(GUID, ForeignKey("user.id", ondelete="SET NULL"))

    chat_room: ChatRoom = relationship("ChatRoom", back_populates="messages")
    chat_room_id = Column(GUID, ForeignKey("chat_room.id", ondelete="SET NULL"))

    text = Column(String(300), nullable=True)
    media_url = Column(String(256), nullable=True)
