"""
All fields in schemas are defaults from FastAPI Users, repeated below for easier view
"""

from datetime import datetime
import uuid
from pydantic import BaseModel, Field

from app.schemas.chat import MessageRead


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
    profile_pic: str | None

    class Config:
        orm_mode = True


class UserListRead(BaseModel):
    total: int
    users: list[UserRead]


class MyInfoRead(UserRead):
    phone_number: str
    age: int | None
    bio: str | None
    weight: int | None
    workout_per_week: int | None
    longitude: float | None
    latitude: float | None
    created_at: datetime
    updated_at: datetime
    is_superuser: bool


class UserCreate(CreateUpdateDictModel):
    phone_number: str
    username: str
    is_superuser: bool = False
    profile_pic: str | None = None
    bio: str | None = None
    age: int | None = None
    weight: int | None = None
    workout_per_week: int | None = None
    longitude: float | None = None
    latitude: float | None = None


class UserUpdate(CreateUpdateDictModel):
    phone_number: str | None
    username: str | None
    profile_pic: str | None
    bio: str | None
    age: int | None
    weight: int | None
    workout_per_week: int | None
    longitude: float | None
    latitude: float | None


class LoginRequest(BaseModel):
    phone_number: str = Field(..., description="Phone number: +821012345678")


class LoginResponse(BaseModel):
    token: str = Field(..., description="Token")
    refresh_token: str = Field(..., description="Refresh token")
