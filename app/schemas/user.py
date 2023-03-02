"""
All fields in schemas are defaults from FastAPI Users, repeated below for easier view
"""
from typing import Optional
from datetime import datetime
import json
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
                "gender",
                "phone_number",
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
    username: str
    age: int | None
    bio: str | None
    gender: str
    weight: int
    height: int
    workout_per_week: int
    workout_level: str
    workout_goal: str | None
    workout_time_per_day: str
    workout_time_period: str
    address: str | None
    created_at: datetime
    updated_at: datetime
    # gym_info: "Optional[GymInfoRead]"
    gym_info: "Optional[GymInfoRead]"


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


class UserUpdate(CreateUpdateDictModel):
    profile_pic: str | None = Field(description="기존 프로필 사진")
    username: str | None = Field(description="닉네임")
    bio: str | None = Field(description="자기소개")
    age: int | None = Field(description="나이")
    weight: int | None = Field(description="몸무게")
    height: int | None = Field(description="키")
    workout_per_week: int | None = Field(description="일주일에 몇 번 운동하는지")
    workout_goal: str | None = Field(description="운동 목표 ex) '다이어트,체중 유지,근육량 증가'")
    workout_level: str | None = Field(description="초급, 중급, 고급")
    workout_time_per_day: str | None = Field(description="하루에 몇 시간 운동하는지")
    workout_time_period: str | None = Field(description="오전, 오후, 저녁 등의 시간")
    gender: str | None = Field(description="성별")
    address: str | None = Field(description="주소")
    gym_info: "Optional[GymInfoBase]" = Field(None, description="헬스장 정보")

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class LoginRequest(BaseModel):
    phone_number: str = Field(..., description="Phone number: 01012345678")


class LoginResponse(BaseModel):
    token: str = Field(..., description="Token")
    refresh_token: str = Field(..., description="Refresh token")
    user_id: uuid.UUID = Field(..., description="User ID")


class RecommendedUser(BaseModel):
    id: uuid.UUID
    profile_pic: str | None
    username: str
    # similarity: float
    class Config:
        orm_mode = True


# if TYPE_CHECKING:
from app.schemas.workout_promise import GymInfoBase, GymInfoRead

UserUpdate.update_forward_refs()
MyInfoRead.update_forward_refs()
