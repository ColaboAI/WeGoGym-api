from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field

from app.schemas.user import UserRead
from app.schemas.workout_promise import WorkoutParticipantRead


## 알림 타입
class NotificationType(str, Enum):
    GENERAL = "GENERAL"
    FRIEND_REQUEST = "FRIEND_REQUEST"
    FRIEND_ACCEPTANCE = "FRIEND_ACCEPTANCE"
    FOLLOW_REQUEST = "FOLLOW_REQUEST"
    FOLLOW_ACCEPTANCE = "FOLLOW_ACCEPTANCE"


## 운동 약속 알림 타입
class NotificationWorkoutType(str, Enum):
    NEW_WORKOUT_PROMISE = "NEW_WORKOUT_PROMISE"
    # 운동 약속 참여 요청 (운동 약속 생성자에게 보내는 알림)
    WORKOUT_REQUEST = "WORKOUT_REQUEST"
    # 운동 약속 참여 승인 (운동 약속 참여자에게 보내는 알림)
    WORKOUT_ACCEPT = "WORKOUT_ACCEPT"
    # 운동 약속 참여 거절 (운동 약속 참여자에게 보내는 알림)
    WORKOUT_REJECT = "WORKOUT_REJECT"
    # 새로운 운동 약속 참가자 (기존의 운동 약속 참여자에게 보내는 알림)
    WORKOUT_NEW_PARTICIPANT = "WORKOUT_NEW_PARTICIPANT"
    # 운동 약속 모집 완료 (운동 약속 참여자 모두에게 보내는 알림)
    WORKOUT_RECRUIT_END = "WORKOUT_RECRUIT_END"


class NotificationBase(BaseModel):
    message: str = Field(..., min_length=1, max_length=100)
    read_at: datetime | None = Field(None, description="읽은 시간")


class NotificationWorkoutBase(NotificationBase):
    notification_type: NotificationWorkoutType = Field(..., description="운동 알림 타입")


class NotificationWorkoutRead(NotificationWorkoutBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    sender_id: UUID = Field(..., description="알림 보낸 사람")
    sender: UserRead
    recipient_id: UUID = Field(..., description="알림 받는 사람")
    recipient: WorkoutParticipantRead

    class Config:
        orm_mode = True


class BaseListResponse(BaseModel):
    total: int | None


class NotificationWorkoutListResponse(BaseListResponse):
    items: list[NotificationWorkoutRead]
    next_cursor: int | None

    class Config:
        orm_mode = True


NotificationWorkoutRead.update_forward_refs()
