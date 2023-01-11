"""
All fields in schemas are defaults from FastAPI Users, repeated below for easier view
"""

from datetime import datetime
from typing import Union
import uuid
from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    username: str
    profile_pic: str


class MyInfoRead(UserRead):
    phone_number: str
    last_active_at: datetime
    username: str
    profile_pic: Union[str, None]
    age: Union[int, None]
    weight: Union[int, None]
    workout_per_week: Union[int, None]
    longitute: Union[float, None]
    latitude: Union[float, None]

    # TODO: return object or id
    # exercise_level_id: uuid.UUID
    # gym_id: uuid.UUID
    # goal_id: uuid.UUID


class UserCreate(schemas.BaseUserCreate):
    phone_number: str
    username: str
    profile_pic: Union[str, None]
    bio: Union[str, None]
    age: Union[int, None]
    weight: Union[int, None]
    workout_per_week: Union[int, None]
    longitute: Union[float, None]
    latitude: Union[float, None]


class UserUpdate(schemas.BaseUserUpdate):
    phone_number: Union[str, None]
    username: Union[str, None]
    profile_pic: Union[str, None]
    bio: Union[str, None]
    age: Union[int, None]
    weight: Union[int, None]
    workout_per_week: Union[int, None]
    longitute: Union[float, None]
    latitude: Union[float, None]
