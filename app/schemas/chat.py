import datetime
from typing import Union
from pydantic import BaseModel
import uuid


class ChatRoomGroupMemberRead(BaseModel):
    id: uuid.uuid4
    user_id: uuid.uuid4
    chatroom_id: uuid.uuid4
    joined_datetime: datetime
    left_datetime: datetime

    class Config:
        orm_mode = True


class ChatRoomGroupMemberCreate(BaseModel):
    user_id: uuid.uuid4
    chatroom_id: uuid.uuid4


class ChatRoomRead(BaseModel):
    id: uuid.uuid4
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
    chatroom_group_members: list[uuid.uuid4]


class ChatRoomUpdate(BaseModel):
    name: Union[str, None]
    description: Union[str, None]
    chatroom_group_members: list[uuid.uuid4]


class MessageRead(BaseModel):
    id: uuid.uuid4
    chatroom_id: uuid.uuid4
    user_id: uuid.uuid4
    text: Union[str, None]
    created_datetime: datetime
    media_url: Union[str, None]

    class Config:
        orm_mode = True


class MessageCreate(BaseModel):
    chatroom_id: uuid.uuid4
    user_id: uuid.uuid4
    text: Union[str, None]
    media_url: Union[str, None]
