from sqlalchemy import TIMESTAMP, Boolean, Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models import Base
import uuid
from app.models.guid import GUID


class ChatRoomMember(Base):
    __tablename__ = "chat_room_member"
    id = Column(GUID, primary_key=True, index=True, default=uuid.uuid4)

    chat_room = relationship("ChatRoom", back_populates="members")
    chat_room_id = Column(
        GUID, ForeignKey("chat_room.id", ondelete="CASCADE"), nullable=False
    )

    user = relationship("User", back_populates="chat_rooms")
    user_id = Column(GUID, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    joined_at = Column(TIMESTAMP, nullable=False)
    left_at = Column(TIMESTAMP, nullable=True)
    is_superuser = Column(Boolean, default=False, nullable=False)


class ChatRoom(Base):
    __tablename__ = "chat_room"
    id = Column(GUID, primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(String(200), nullable=False)
    created_by = Column(GUID, nullable=False, default=uuid.uuid4)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False)

    members = relationship(
        "ChatRoomMember",
        back_populates="chat_room",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )

    messages = relationship(
        "Message",
        back_populates="chat_room",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )


# 유저 삭제 및 채팅방 삭제 시, text는 삭제되지 않음.
class Message(Base):
    __tablename__ = "message"
    id = Column(GUID, primary_key=True, index=True, default=uuid.uuid4)

    user = relationship("User", back_populates="messages")
    user_id = Column(GUID, ForeignKey("user.id", ondelete="SET NULL"))

    chat_room = relationship("ChatRoom", back_populates="messages")
    chat_room_id = Column(GUID, ForeignKey("chat_room.id", ondelete="SET NULL"))

    text = Column(String(300), nullable=True)
    media_url = Column(String(256), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False)
