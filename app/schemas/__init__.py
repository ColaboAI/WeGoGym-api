from .user import *
from .audio import *
from .chat import *
from .workout_promise import *
from .voc import *
from .community import *


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
    "WorkoutParticipantUpdate",
    "WorkoutPromiseBase",
    "WorkoutPromiseRead",
    "WorkoutPromiseUpdate",
]


class ExceptionResponseSchema(BaseModel):
    error: str = Field(..., description="Error message")
