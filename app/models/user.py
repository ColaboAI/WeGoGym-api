"""
SQL Alchemy models declaration.

Note, imported by alembic migrations logic, see `alembic/env.py`
"""

from typing import Union

from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import relationship

from app.models import Base
from app.models.chat import ChatRoom, Message
from app.models.guid import GUID
import uuid


class User(Base):
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    username: str = Column(String(100), nullable=False)
    phone_number: str = Column(String(100), nullable=False)
    profile_pic: Union[str, None] = Column(String(100))
    bio: Union[str, None] = Column(String(100))
    age: Union[int, None] = Column(Integer)
    weight: Union[int, None] = Column(Integer)
    longitude: Union[float, None] = Column(Float)
    latitude: Union[float, None] = Column(Float)
    last_active_at: Union[int, None] = Column(Integer)
    workout_per_week: Union[int, None] = Column(Integer)

    chat_rooms: list[ChatRoom] = relationship(
        "ChatRoom",
        lazy="joined",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )
    messages: list[Message] = relationship(
        "Message",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )
