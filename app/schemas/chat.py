from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID
from app.schemas.user import UserRead


class ChatRoomMemberRead(BaseModel):
    id: UUID
    is_admin: bool
    created_at: datetime
    last_read_at: datetime

    class Config:
        orm_mode = True


class ChatRoomMemberReadWithUser(ChatRoomMemberRead):
    user: UserRead


class ChatRoomMemberCreate(BaseModel):
    user_id: UUID
    chat_room_id: UUID


class ChatRoomMemberUpdate(BaseModel):
    user_id: UUID
    chat_room_id: UUID
    is_admin: bool


class ChatRoomRead(BaseModel):
    id: UUID
    name: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime
    is_private: bool
    unread_count: int | None

    class Config:
        orm_mode = True


class ChatRoomReadWithLastMessageAndMembers(ChatRoomRead):
    last_message_text: str | None
    last_message_created_at: datetime | None
    members: list[ChatRoomMemberReadWithUser]


class ChatRoomList(BaseModel):
    total: int
    items: list[ChatRoomRead]

    class Config:
        orm_mode = True


class MyChatRoomList(BaseModel):
    total: int
    items: list[ChatRoomReadWithLastMessageAndMembers]

    class Config:
        orm_mode = True


class ChatRoomMemberList(BaseModel):
    total: int
    items: list[ChatRoomMemberRead]


# TODO: ChatRoomWithMembersRead vs ChatRoomReadWithLastMessageAndMembers
class ChatRoomWithMembersRead(BaseModel):
    id: UUID
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    is_private: bool
    members: list[ChatRoomMemberRead]

    class Config:
        orm_mode = True


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

    created_by: UUID = Field(
        ...,
        description="User ID of user who created chat room",
    )
    members_user_id: list[UUID] = Field(
        [],
        description="List of user IDs of members of chat room",
    )

    is_private: bool = Field(
        False,
        description="Is chat room private",
    )


class ChatRoomUpdate(BaseModel):
    name: str | None
    description: str | None
    chat_room_members: list[UUID]


class MessageRead(BaseModel):
    id: UUID
    chat_room_id: UUID
    user_id: UUID
    text: str | None
    created_at: datetime
    media_url: str | None

    class Config:
        orm_mode = True


class MessageListRead(BaseModel):
    total: int
    items: list[MessageRead]


class MessageCreate(BaseModel):
    chat_room_id: UUID
    user_id: UUID
    text: str | None
    media_url: str | None


class ChatRoomCreateResponse(BaseModel):
    name: str
    description: str

    class Config:
        orm_mode = True
