from .user import *
from .audio import *
from .chat import *

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
]


class ExceptionResponseSchema(BaseModel):
    error: str = Field(..., description="Error message")
