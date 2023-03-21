from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field


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
