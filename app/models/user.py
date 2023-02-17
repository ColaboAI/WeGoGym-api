"""
SQL Alchemy models declaration.

Note, imported by alembic migrations logic, see `alembic/env.py`
"""


from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship
from app.core.db.mixins.timestamp_mixin import TimestampMixin

from app.models import Base
from app.models.chat import ChatRoom, Message
from app.models.guid import GUID
import uuid

from app.models.workout_promise import WorkoutParticipant


class User(TimestampMixin, Base):  # type: ignore
    __tablename__ = "user"
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    username = Column(String(100), nullable=False, unique=True, index=True)
    phone_number = Column(String(100), nullable=False)
    is_superuser = Column(Boolean, server_default=expression.false(), nullable=False)
    profile_pic = Column(String(255), nullable=True)
    bio = Column(String(100), nullable=True)
    age = Column(Integer, server_default=text("0"), nullable=False)
    weight = Column(Integer, server_default=text("0"), nullable=False)
    height = Column(Integer, server_default=text("0"), nullable=False)
    gender = Column(String(50), server_default="other", nullable=False)
    workout_per_week = Column(Integer, server_default=text("0"), nullable=False)
    workout_level = Column(String(100), nullable=True)
    workout_goal = Column(String(255), nullable=True)
    workout_time_per_day = Column(String(100), nullable=True)
    workout_time_period = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)

    # Child relationship with GymInfo ("many" to one)
    gym_info_id = Column(GUID, ForeignKey("gym_info.id", ondelete="SET NULL"))
    gym_info = relationship("GymInfo", back_populates="users")

    # Parent relationship with ChatRoomMember (Many to "One")
    chat_room_members: list[ChatRoom] = relationship(
        "ChatRoomMember",
        back_populates="user",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )
    # Parent relationship with Message (Many to "One")
    messages: list[Message] = relationship(
        "Message",
        back_populates="user",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )

    # Parent relationship with WorkoutParticipant (Many to "One")
    workout_participants: list[WorkoutParticipant] = relationship(
        "WorkoutParticipant",
        back_populates="user",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )
