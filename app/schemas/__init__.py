from .user import *
from .audio import *
from .chat import *
from .workout_promise import *

__all__ = [
    "UserRead",
    "UserCreate",
    "UserUpdate",
    "AudioRead",
    "AudioCreate",
    "ChatRoomRead",
    "ChatRoomCreate",
    "ChatRoomUpdate",
    "MessageRead",
    "MessageCreate",
    "MessageUpdate",
    "ChatRoomMemberRead",
    "ChatRoomMemberCreate",
    "ChatRoomMemberUpdate",
    "LoginResponseSchema",
    "ChatRoomCreateResponse",
    "ParticipantStatus",
    "WorkoutParticipantBase",
    "WorkoutParticipantRead",
    "WorkoutParticipantCreate",
    "WorkoutParticipantUpdate",
    "WorkoutPromiseBase",
    "WorkoutPromiseRead",
    "WorkoutPromiseCreate",
    "WorkoutPromiseUpdate",
]


class ExceptionResponseSchema(BaseModel):
    error: str = Field(..., description="Error message")
