import datetime
from typing import Union
from pydantic import BaseModel
from uuid import UUID


class ChatRoomGroupMemberRead(BaseModel):
    id: UUID
    user_id: UUID
    chatroom_id: UUID
    joined_datetime: datetime
    left_datetime: datetime

    class Config:
        orm_mode = True


class ChatRoomGroupMemberCreate(BaseModel):
    user_id: UUID
    chatroom_id: UUID


class ChatRoomRead(BaseModel):
    id: UUID
    name: str
    description: str
    created_datetime: datetime
    updated_datetime: datetime
    chatroom_group_members: list[ChatRoomGroupMemberRead]

    class Config:
        orm_mode = True


class ChatRoomCreate(BaseModel):
    name: str
    description: str
    chatroom_group_members: list[UUID]


class ChatRoomUpdate(BaseModel):
    name: Union[str, None]
    description: Union[str, None]
    chatroom_group_members: list[UUID]


class MessageRead(BaseModel):
    id: UUID
    chatroom_id: UUID
    user_id: UUID
    text: Union[str, None]
    created_datetime: datetime
    media_url: Union[str, None]

    class Config:
        orm_mode = True


class MessageCreate(BaseModel):
    chatroom_id: UUID
    user_id: UUID
    text: Union[str, None]
    media_url: Union[str, None]
