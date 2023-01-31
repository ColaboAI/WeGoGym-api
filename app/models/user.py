"""
SQL Alchemy models declaration.

Note, imported by alembic migrations logic, see `alembic/env.py`
"""


from sqlalchemy import Boolean, Column, Float, Integer, String
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship
from app.core.db.mixins.timestamp_mixin import TimestampMixin

from app.models import Base
from app.models.chat import ChatRoom, Message
from app.models.guid import GUID
import uuid


class User(TimestampMixin, Base):
    __tablename__ = "user"
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    username: str = Column(String(100), nullable=False)
    phone_number: str = Column(String(100), nullable=False)
    is_superuser: bool = Column(
        Boolean, server_default=expression.false(), nullable=False
    )
    profile_pic: str | None = Column(String(100), nullable=True)
    bio: str | None = Column(String(100), nullable=True)
    age: int | None = Column(Integer, nullable=True)
    weight: int | None = Column(Integer, nullable=True)
    longitude: float | None = Column(Float, nullable=True)
    latitude: float | None = Column(Float, nullable=True)
    workout_per_week: int | None = Column(Integer, nullable=True)

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
