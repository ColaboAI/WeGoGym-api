from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class ChatRoomMemberRead(BaseModel):
    id: UUID
    user_id: UUID
    chat_room_id: UUID
    joined_at: datetime
    left_at: datetime | None

    class Config:
        orm_mode = True


class ChatRoomMemberCreate(BaseModel):
    user_id: UUID
    chat_room_id: UUID


class ChatRoomMemberUpdate(BaseModel):
    user_id: UUID
    chat_room_id: UUID


class ChatRoomRead(BaseModel):
    id: UUID
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    chat_room_members: list[ChatRoomMemberRead]

    class Config:
        orm_mode = True


class ChatRoomCreate(BaseModel):
    name: str
    description: str
    creator_id: UUID
    members_user_id: list[UUID]


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


class MessageCreate(BaseModel):
    chat_room_id: UUID
    user_id: UUID
    text: str | None
    media_url: str | None
