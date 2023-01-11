from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base
import uuid
from fastapi_users_db_sqlalchemy import GUID


class ChatRoomMember(Base):
    __tablename__ = "chat_group_member"
    id = Column(GUID, primary_key=True, index=True, default=uuid.uuid4)
    chat_room = relationship("ChatRoom", back_populates="members")
    user = relationship("User", back_populates="chat_rooms")
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


class Message(Base):
    __tablename__ = "message"
    id = Column(GUID, primary_key=True, index=True, default=uuid.uuid4)
    user = relationship("User", back_populates="messages")
    chat_room = relationship("ChatRoom", back_populates="messages")
    text = Column(String(300), nullable=True)
    media_url = Column(String(256), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False)
