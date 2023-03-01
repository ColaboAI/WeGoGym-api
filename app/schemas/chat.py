from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class ChatRoomMemberRead(BaseModel):
    id: UUID
    user_id: UUID
    chat_room_id: UUID
    is_admin: bool
    created_at: datetime
    last_read_at: datetime
    last_message_text: str | None
    last_message_created_at: datetime | None

    class Config:
        orm_mode = True


class ChatRoomMemberCreate(BaseModel):
    user_id: UUID
    chat_room_id: UUID


class ChatRoomMemberUpdate(BaseModel):
    user_id: UUID
    chat_room_id: UUID
    is_admin: bool


class ChatRoomRead(BaseModel):
    id: UUID
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    is_private: bool

    class Config:
        orm_mode = True


class ChatRoomList(BaseModel):
    total: int
    rooms: list[ChatRoomRead]


class ChatRoomMemberList(BaseModel):
    total: int
    members: list[ChatRoomMemberRead]


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
    name: str
    description: str
    created_by: UUID
    members_user_id: list[UUID]
    is_private: bool


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


class MessateListRead(BaseModel):
    total: int
    messages: list[MessageRead]


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
