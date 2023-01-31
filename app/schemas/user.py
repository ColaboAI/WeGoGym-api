"""
All fields in schemas are defaults from FastAPI Users, repeated below for easier view
"""

from datetime import datetime
import uuid
from pydantic import BaseModel, Field


class CreateUpdateDictModel(BaseModel):
    def create_update_dict(self):
        return self.dict(
            exclude_unset=True,
            exclude={
                # TODO: 일반적인 update에서 수정 불가능한 필드 설정
                "id",
                "is_superuser",
                "created_at",
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
    profile_pic: str | None
    age: int | None
    weight: int | None
    workout_per_week: int | None
    longitute: float | None
    latitude: float | None

    # TODO: return object or id
    # exercise_level_id: uuid.UUID
    # gym_id: uuid.UUID
    # goal_id: uuid.UUID


class UserCreate(CreateUpdateDictModel):
    phone_number: str
    username: str
    is_superuser: bool = False
    profile_pic: str | None
    bio: str | None
    age: int | None
    weight: int | None
    workout_per_week: int | None
    longitute: float | None
    latitude: float | None


class UserUpdate(CreateUpdateDictModel):
    phone_number: str | None
    username: str | None
    profile_pic: str | None
    bio: str | None
    age: int | None
    weight: int | None
    workout_per_week: int | None
    longitute: float | None
    latitude: float | None


class LoginResponseSchema(BaseModel):
    token: str = Field(..., description="Token")
    refresh_token: str = Field(..., description="Refresh token")
