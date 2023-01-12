"""
All fields in schemas are defaults from FastAPI Users, repeated below for easier view
"""

from datetime import datetime
from typing import Union
import uuid
from pydantic import BaseModel


class CreateUpdateDictModel(BaseModel):
    def create_update_dict(self):
        return self.dict(
            exclude_unset=True,
            exclude={
                # TODO: 일반적인 update에서 수정 불가능한 필드 설정
                "id"
            },
        )

    def create_update_dict_superuser(self):
        return self.dict(exclude_unset=True, exclude={"id"})


class UserRead(CreateUpdateDictModel):
    id: uuid.UUID
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


class UserCreate(CreateUpdateDictModel):
    phone_number: str
    username: str
    profile_pic: Union[str, None]
    bio: Union[str, None]
    age: Union[int, None]
    weight: Union[int, None]
    workout_per_week: Union[int, None]
    longitute: Union[float, None]
    latitude: Union[float, None]


class UserUpdate(CreateUpdateDictModel):
    phone_number: Union[str, None]
    username: Union[str, None]
    profile_pic: Union[str, None]
    bio: Union[str, None]
    age: Union[int, None]
    weight: Union[int, None]
    workout_per_week: Union[int, None]
    longitute: Union[float, None]
    latitude: Union[float, None]
