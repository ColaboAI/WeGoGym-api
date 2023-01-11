"""
All fields in schemas are defaults from FastAPI Users, repeated below for easier view
"""

import datetime
import uuid
from fastapi_users import schemas

from pydantic import EmailStr


class UserRead(schemas.BaseUser[uuid.UUID]):
    username: str
    profile_pic: str


class MyInfoRead(UserRead):
    phone_number: str
    last_active_at: datetime
    username: str
    profile_pic: str
    age: int
    weight: int
    workout_per_week: int
    longitute: float
    latitude: float

    # TODO: return object or id
    # exercise_level_id: uuid.UUID
    # gym_id: uuid.UUID
    # goal_id: uuid.UUID


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass
