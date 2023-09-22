from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, UUID4

from app.schemas.user import UserRead


class ChatRoomMemberRead(BaseModel):
    id: UUID4
    is_admin: bool
    created_at: datetime
    last_read_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class ChatRoomMemberReadWithUser(ChatRoomMemberRead):
    user: UserRead


class ChatRoomMemberCreate(BaseModel):
    user_id: UUID4
    chat_room_id: UUID4


class ChatRoomMemberUpdate(BaseModel):
    user_id: UUID4
    chat_room_id: UUID4
    is_admin: bool


class ChatRoomRead(BaseModel):
    id: UUID4
    name: str | None = None
    description: str | None = None
    created_at: datetime
    updated_at: datetime
    is_private: bool
    is_group_chat: bool
    unread_count: int | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class ChatRoomReadWithLastMessageAndMembers(ChatRoomRead):
    last_message_text: str | None
    last_message_created_at: datetime | None
    members: list[ChatRoomMemberReadWithUser]


class ChatRoomList(BaseModel):
    total: int
    items: list[ChatRoomRead]

    model_config = ConfigDict(
        from_attributes=True,
    )


class MyChatRoomList(BaseModel):
    total: int | None
    next_cursor: int | None
    items: list[ChatRoomReadWithLastMessageAndMembers]

    model_config = ConfigDict(
        from_attributes=True,
    )


class ChatRoomMemberList(BaseModel):
    total: int
    items: list[ChatRoomMemberRead]


# TODO: ChatRoomWithMembersRead vs ChatRoomReadWithLastMessageAndMembers
class ChatRoomWithMembersRead(ChatRoomRead):
    members: list[ChatRoomMemberReadWithUser]

    model_config = ConfigDict(
        from_attributes=True,
    )


class ChatRoomCreate(BaseModel):
    name: str | None = Field(
        None,
        max_length=100,
        description="Name of chat room",
    )
    description: str | None = Field(
        None,
        max_length=100,
        description="Description of chat room",
    )

    admin_user_id: UUID4 = Field(
        ...,
        description="User ID of user who created chat room",
    )
    members_user_ids: list[UUID4] = Field(
        ...,
        description="List of user IDs of members of chat room",
    )

    is_private: bool = Field(
        False,
        description="Is chat room private",
    )
    is_group_chat: bool = Field(
        ...,
        description="Is chat room group chat",
    )

    retry: bool = Field(
        False,
        description="Retry creating chat room",
    )

    workout_promise_id: UUID4 | None = Field(
        None,
        description="Workout Promise ID of chat room",
    )


class ChatRoomUpdate(BaseModel):
    name: str | None
    description: str | None
    chat_room_members: list[UUID4]


class MessageRead(BaseModel):
    id: UUID4
    chat_room_id: UUID4
    user_id: UUID4 | None
    text: str | None
    created_at: datetime
    media_url: str | None

    model_config = ConfigDict(
        from_attributes=True,
    )


class MessageListRead(BaseModel):
    total: int
    next_cursor: int | None
    items: list[MessageRead]


class MessageCreate(BaseModel):
    chat_room_id: UUID4
    user_id: UUID4
    text: str | None
    media_url: str | None
