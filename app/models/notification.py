from datetime import datetime
from typing import TYPE_CHECKING
import uuid
from pydantic import UUID4
from sqlalchemy import DateTime, String, ForeignKey

from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.db.mixins.timestamp_mixin import TimestampMixin
from app.models.base import Base
from app.models.guid import GUID
from app.schemas.notification import NotificationWorkoutType
from app.utils.generics import utcnow


if TYPE_CHECKING:
    from . import WorkoutParticipant


class Notification(TimestampMixin, Base):
    id: Mapped[UUID4] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    # 메세지 내용이 담겨 있음
    message: Mapped[str] = mapped_column(String, nullable=True)
    # 메세지를 읽었는지 여부에 따라 프론트에서 알림 보여주는 방식을 달리하기 위함
    read_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=utcnow(), nullable=True)


# NotificationWorkout inherits from Notification
class NotificationWorkout(Notification):
    # One to One relationship with Notification
    id: Mapped[UUID4] = mapped_column(GUID, ForeignKey("notification.id"), primary_key=True)
    notification_type: Mapped[str] = mapped_column(
        String, default=NotificationWorkoutType.NEW_WORKOUT_PROMISE, nullable=False
    )

    # 알림을 보내는 유저(WorkoutParticipant) Many to One
    sender_id: Mapped[UUID4] = mapped_column(
        GUID, ForeignKey("workout_participant.id", ondelete="CASCADE"), nullable=False
    )
    sender: Mapped["WorkoutParticipant"] = relationship(
        "WorkoutParticipant",
        back_populates="notifications_workout_sender",
        foreign_keys=[sender_id],
        lazy="select",
    )

    # 알림을 수신하는 유저들(WorkoutParticipants) Many to One
    recipient_id: Mapped[UUID4] = mapped_column(
        GUID, ForeignKey("workout_participant.id", ondelete="CASCADE"), nullable=False
    )
    recipient: Mapped["WorkoutParticipant"] = relationship(
        "WorkoutParticipant",
        back_populates="notifications_workout_recipient",
        foreign_keys=[recipient_id],
        lazy="select",
    )
