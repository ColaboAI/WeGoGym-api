import datetime
from typing import Union
from pydantic import BaseModel
from uuid import UUID


class ChatRoomMemberRead(BaseModel):
    id: UUID
    user_id: UUID
    chat_room_id: UUID
    joined_datetime: datetime
    left_datetime: datetime

    class Config:
        orm_mode = True


class ChatRoomMemberCreate(BaseModel):
    user_id: UUID
    chat_room_id: UUID


class ChatRoomRead(BaseModel):
    id: UUID
    name: str
    description: str
    created_datetime: datetime
    updated_datetime: datetime
    chat_room_members: list[ChatRoomMemberRead]

    class Config:
        orm_mode = True


class ChatRoomCreate(BaseModel):
    name: str
    description: str
    chat_room_members: list[UUID]


class ChatRoomUpdate(BaseModel):
    name: Union[str, None]
    description: Union[str, None]
    chat_room_members: list[UUID]


class MessageRead(BaseModel):
    id: UUID
    chat_room_id: UUID
    user_id: UUID
    text: Union[str, None]
    created_datetime: datetime
    media_url: Union[str, None]

    class Config:
        orm_mode = True


class MessageCreate(BaseModel):
    chat_room_id: UUID
    user_id: UUID
    text: Union[str, None]
    media_url: Union[str, None]
