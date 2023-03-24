from typing import TYPE_CHECKING
import uuid
from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db.mixins.timestamp_mixin import TimestampMixin
from app.models.base import Base
from app.models.guid import GUID
from app.schemas.notification import NotificationWorktoutType


if TYPE_CHECKING:
    from . import User, WorkoutParticipant


class Notification(TimestampMixin, Base):
    __tablename__ = "notification"
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    # 메세지 내용이 담겨 있음
    message = Column(String, nullable=False)
    # 메세지를 읽었는지 여부에 따라 프론트에서 알림 보여주는 방식을 달리하기 위함
    read_at = Column(DateTime, default=None, nullable=True)


# NotificationWorkout inherits from Notification
class NotificationWorkout(Notification):
    __tablename__ = "notification_workout"
    # One to One relationship with Notification
    id = Column(GUID, ForeignKey("notification.id"), primary_key=True)
    notification_type = Column(
        String, default=NotificationWorktoutType.NEW_WORKOUT_PROMISE, nullable=False
    )

    # 알림을 보내는 유저 Many to One
    sender_id = Column(GUID, ForeignKey("user.id", ondelete="SET NULL"), nullable=False)
    sender: "User" = relationship(
        "User", back_populates="notifications_workout", lazy="select"
    )

    # 알림을 수신하는 유저들(WorkoutParticipants) Many to One
    recipient_id = Column(
        GUID, ForeignKey("workout_participant.id", ondelete="SET NULL"), nullable=False
    )
    recipient: "WorkoutParticipant" = relationship(
        "WorkoutParticipant", back_populates="notifications_workout", lazy="select"
    )
