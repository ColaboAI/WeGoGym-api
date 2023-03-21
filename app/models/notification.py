from typing import TYPE_CHECKING
from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db.mixins.timestamp_mixin import TimestampMixin
from app.models import Base
from app.models.guid import GUID
import uuid
from app.models.user import User
from app.models.workout_promise import WorkoutPromise
from app.schemas.notification import NotificationType


if TYPE_CHECKING:
    from . import User


class Notification(TimestampMixin, Base):
    __tablename__ = "notification"
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    # 메세지 내용이 담겨 있음
    # ex) "{참여자} : {참여자의 메세지}"
    # ex) "참가 요청이 승인되었습니다."
    message = Column(String, nullable=False)
    # 알림의 유형에 따라 프론트에서 보여 주는 방식을 달리할 수 있음
    notification_type = Column(String, default=NotificationType.GENERAL, nullable=False)
    # 알림을 수신하는 유저
    recipient_id = Column(
        GUID, ForeignKey("user.id", ondelete="SET NULL"), nullable=False
    )
    recipient: User = relationship(
        "User", back_populates="notifications", lazy="select"
    )
    # 메세지를 읽었는지 여부에 따라 프론트에서 알림 보여주는 방식을 달리하기 위함
    read_at = Column(DateTime, default=None, nullable=True)
