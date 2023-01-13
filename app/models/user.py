"""
SQL Alchemy models declaration.

Note, imported by alembic migrations logic, see `alembic/env.py`
"""


from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import relationship

from app.models import Base
from app.models.chat import ChatRoom, Message
from app.models.guid import GUID
import uuid


class User(Base):
    __tablename__ = "user"
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    username: str = Column(String(100), nullable=False)
    phone_number: str = Column(String(100), nullable=False)
    profile_pic: str | None = Column(String(100))
    bio: str | None = Column(String(100))
    age: int | None = Column(Integer)
    weight: int | None = Column(Integer)
    longitude: float | None = Column(Float)
    latitude: float | None = Column(Float)
    last_active_at: int | None = Column(Integer)
    workout_per_week: int | None = Column(Integer)

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
