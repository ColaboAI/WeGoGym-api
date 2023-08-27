from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, UUID4

from app.schemas.workout_promise import WorkoutParticipantRead


## 알림 타입
class NotificationType(str, Enum):
    GENERAL = "GENERAL"
    FRIEND_REQUEST = "FRIEND_REQUEST"
    FRIEND_ACCEPTANCE = "FRIEND_ACCEPTANCE"
    FOLLOW_REQUEST = "FOLLOW_REQUEST"
    FOLLOW_ACCEPTANCE = "FOLLOW_ACCEPTANCE"


class NotificationWorkoutTitle(str, Enum):
    NEW_WORKOUT_PROMISE = "새로운 운동 약속이 생성되었습니다."
    WORKOUT_REQUEST = "새로운 참여 요청이 있습니다."
    WORKOUT_NEW_PARTICIPANT = "새로운 참여자가 있습니다."
    NEW_COMMENT = "운동 약속에 새로운 댓글이 달렸습니다."
    WORKOUT_REJECT = "참여 요청이 거절되었습니다."
    WORKOUT_ACCEPT = "참여 요청이 승인되었습니다."
    # TODO: 어감 이상. 다른 표현으로 바꿔야 함.
    WORKOUT_CANCEL_PARTICIPANT = "약속 참여를 취소한 사람이 있습니다."

    CANCEL_WORKOUT = "운동 약속이 취소되었습니다."


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

    # 기존 참여자가 취소 (운동 약속 참여자에게 보내는 알림)
    WORKOUT_CANCEL_PARTICIPANT = "CANCEL_PARTICIPANT"
    # 운동 약속 취소 (운동 약속 참여자에게 보내는 알림)
    CANCEL_WORKOUT = "CANCEL_WORKOUT"


class NotificationBase(BaseModel):
    message: str | None = Field(None, min_length=1, max_length=100)
    read_at: datetime | None = Field(None, description="읽은 시간")

    class Config:
        orm_mode = True


class NotificationWorkoutBase(NotificationBase):
    notification_type: NotificationWorkoutType = Field(..., description="운동 알림 타입")

    class Config:
        orm_mode = True


class NotificationWorkoutRead(NotificationWorkoutBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    sender_id: UUID4 = Field(..., description="알림 보낸 사람")
    sender: WorkoutParticipantRead
    recipient_id: UUID4 = Field(..., description="알림 받는 사람")
    recipient: WorkoutParticipantRead

    class Config:
        orm_mode = True


class NotificationWorkoutUpdate(BaseModel):
    message: str | None = Field(None, min_length=1, max_length=100)
    read_at: datetime | None = Field(None, description="읽은 시간")

    def get_update_dict(self):
        return self.model_dump(
            exclude_unset=True,
            exclude={
                "id",
                "created_at",
                "updated_at",
            },
        )


class BaseListResponse(BaseModel):
    total: int | None


class NotificationWorkoutListResponse(BaseListResponse):
    items: list[NotificationWorkoutRead]
    next_cursor: int | None

    class Config:
        orm_mode = True


NotificationWorkoutRead.update_forward_refs()
