"""
All fields in schemas are defaults from FastAPI Users, repeated below for easier view
"""
from typing import Optional
from datetime import datetime
import json
from pydantic import BaseModel, Field, UUID4


class CreateUpdateDictModel(BaseModel):
    def update_dict(self):
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
    id: UUID4
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
    age: str | None
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
    profile_pic: str | None = Field(None, description="프로필 사진")
    username: str = Field(..., description="닉네임")
    is_superuser: bool = False
    gender: str = Field(..., description="성별")
    age: str = Field(..., description="나이")
    weight: int = Field(..., description="몸무게")
    height: int = Field(..., description="키")
    workout_per_week: int = Field(..., description="일주일에 몇 번 운동하는지")
    workout_goal: str | None = Field(description="운동 목표 ex) '다이어트,체중 유지,근육량 증가'")
    workout_level: str = Field(..., description="초급, 중급, 고급")
    workout_time_per_day: str = Field(..., description="하루에 몇 시간 운동하는지")
    workout_time_period: str = Field(..., description="오전, 오후, 저녁 등의 시간")
    workout_style: str = Field(..., description="유산소, 근력 운동 등의 운동 스타일")
    workout_routine: str = Field(..., description="3분할, 4분할 등의 운동 루틴")
    workout_partner_gender: str = Field(..., description="선호하는 운동 파트너 성별")
    city: str = Field(..., description="시/도")
    district: str = Field(..., description="구/군")

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class UserUpdate(CreateUpdateDictModel):
    profile_pic: str | None = Field(None, description="기존 프로필 사진")
    username: str | None = Field(None, description="닉네임")
    bio: str | None = Field(None, description="자기소개")
    age: str | None = Field(None, description="나이")
    weight: int | None = Field(None, description="몸무게")
    height: int | None = Field(None, description="키")
    workout_per_week: int | None = Field(None, description="일주일에 몇 번 운동하는지")
    workout_goal: str | None = Field(None, description="운동 목표 ex) '다이어트,체중 유지,근육량 증가'")
    workout_level: str | None = Field(None, description="초급, 중급, 고급")
    workout_time_per_day: str | None = Field(None, description="하루에 몇 시간 운동하는지")
    workout_time_period: str | None = Field(None, description="오전, 오후, 저녁 등의 시간")
    gender: str | None = Field(None, description="성별")
    address: str | None = Field(None, description="주소")
    gym_info: "Optional[GymInfoBase]" = Field(None, description="헬스장 정보")
    fcm_token: str | None = Field(None, description="FCM Token")
    last_active_at: datetime | None = Field(None, description="마지막 활동 시간")

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
    user_id: UUID4 = Field(..., description="User ID")


class RecommendedUser(BaseModel):
    id: UUID4
    profile_pic: str | None
    username: str

    # similarity: float
    class Config:
        orm_mode = True


class CheckUserInfoResponse(BaseModel):
    phone_number_exists: bool | None
    username_exists: bool | None


# if TYPE_CHECKING:
from app.schemas.workout_promise import GymInfoBase, GymInfoRead

UserUpdate.update_forward_refs()
MyInfoRead.update_forward_refs()
