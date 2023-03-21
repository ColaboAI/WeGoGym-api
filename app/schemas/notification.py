from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field

from app.schemas.user import UserRead


class NotificationType(str, Enum):
    GENERAL = "GENERAL"
    NEW_WORKOUT_PROMISE = "NEW_WORKOUT_PROMISE"
    # 운동 약속 참여 요청 (운동 약속 생성자에게 보내는 알림)
    WORKOUT_REQUEST = "WORKOUT_REQUEST"
    # 운동 약속 참여 승인 (운동 약속 참여자에게 보내는 알림)
    WORKOUT_APPROVAL = "WORKOUT_APPROVAL"
    # 운동 약속 참여 거절 (운동 약속 참여자에게 보내는 알림)
    WORKOUT_REJECTION = "WORKOUT_REJECTION"
    # 운동 약속 모집 완료 (운동 약속 참여자 모두에게 보내는 알림)
    WORKOUT_RECRUIT_END = "WORKOUT_RECRUIT_END"
    # 운동 약속 참여자가 취소 (운동 약속 생성자에게 보내는 알림)
    WORKOUT_PARTICIPANT_CANCEL = "WORKOUT_PARTICIPANT_CANCEL"

    NEW_MESSAGE = "NEW_MESSAGE"
    FRIEND_REQUEST = "FRIEND_REQUEST"
    FRIEND_ACCEPTANCE = "FRIEND_ACCEPTANCE"
    FOLLOW_REQUEST = "FOLLOW_REQUEST"
    FOLLOW_ACCEPTANCE = "FOLLOW_ACCEPTANCE"


class NotificationBase(BaseModel):
    message: str = Field(..., min_length=1, max_length=100)
    notification_type: NotificationType = Field(...)
    read_at: datetime | None = Field(None)


class NotificationRead(NotificationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    recipient_id: UUID
    recipient: UserRead

    class Config:
        orm_mode = True


class NotificationUpdate(BaseModel):
    message: str | None = Field(None, min_length=1, max_length=100)
    notification_type: NotificationType | None = Field(None)
    read_at: datetime | None = Field(None)

    def get_update_dict(self):
        return self.dict(
            exclude_unset=True,
            exclude={"id", "created_at", "updated_at", "recipient_id"},
        )


class BaseListResponse(BaseModel):
    total: int | None


class NotificationListResponse(BaseListResponse):
    items: list[NotificationRead]
    next_cursor: int | None

    class Config:
        orm_mode = True


NotificationRead.update_forward_refs()
