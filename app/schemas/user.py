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
    created_at: datetime
    updated_at: datetime
    is_superuser: bool


class UserCreate(CreateUpdateDictModel):
    phone_number: str = Field(..., description="Phone number: 01012345678")
    username: str = Field(..., description="닉네임")
    is_superuser: bool = False
    age: int = Field(..., description="나이")
    weight: int = Field(..., description="몸무게")
    height: int = Field(..., description="키")
    workout_per_week: int = Field(..., description="일주일에 몇 번 운동하는지")
    workout_goal: str | None = Field(description="운동 목표 ex) '다이어트,체중 유지,근육량 증가'")
    workout_level: str = Field(..., description="초급, 중급, 고급")
    workout_time_per_day: str = Field(..., description="하루에 몇 시간 운동하는지")
    workout_time_period: str = Field(..., description="오전, 오후, 저녁 등의 시간")
    gender: str = Field(..., description="성별")


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
    phone_number: str = Field(..., description="Phone number: 01012345678")


class LoginResponse(BaseModel):
    token: str = Field(..., description="Token")
    refresh_token: str = Field(..., description="Refresh token")
