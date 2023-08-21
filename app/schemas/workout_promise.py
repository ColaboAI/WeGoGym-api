from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, UUID4
from app.schemas.chat import ChatRoomRead
from app.schemas.user import UserRead

# from app.schemas.user import UserRead


class WorkoutPromiseStatus(str, Enum):
    RECRUITING = "RECRUITING"
    RECRUIT_ENDED = "RECRUIT_ENDED"
    CANCELLED = "CANCELLED"
    FINISHED = "FINISHED"


class ParticipantStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class GymInfoBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    address: str = Field(..., min_length=1, max_length=100)
    zip_code: str | None = Field(None, max_length=100)
    status: str | None = Field(None)


class GymInfoUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    address: str | None = Field(None, min_length=1, max_length=100)
    zip_code: str | None = Field(None, min_length=1, max_length=100)
    status: str | None = Field(None)

    def get_update_dict(self):
        return self.dict(
            exclude_unset=True,
            exclude={
                "id",
                "created_at",
                "updated_at",
                "address",
                "zip_code",
            },
        )


class GymInfoRead(GymInfoBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class PromiseLocationBase(BaseModel):
    place_name: str = Field(..., min_length=1, max_length=100)
    address: str = Field(..., min_length=1, max_length=100)
    latitude: float | None = Field(None)
    longitude: float | None = Field(None)


class PromiseLocationUpdate(BaseModel):
    place_name: str | None = Field(None, min_length=1, max_length=100)
    address: str | None = Field(None, min_length=1, max_length=100)
    latitude: float | None = Field(None)
    longitude: float | None = Field(None)

    def get_update_dict(self):
        return self.dict(
            exclude_unset=True,
            exclude={
                "id",
                "created_at",
                "updated_at",
            },
        )


class PromiseLocationRead(PromiseLocationBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class WorkoutPromiseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)
    is_private: bool = Field(False, description="Is Private workout promise?")
    max_participants: int = Field(..., ge=1, le=10)
    promise_time: datetime = Field(...)
    recruit_end_time: datetime | None = Field(None, description="Recruit end time")
    workout_part: str | None = Field(None, description="Workout part")


class WorkoutPromiseRead(WorkoutPromiseBase):
    id: UUID4
    chat_room_id: UUID4 | None
    chat_room: ChatRoomRead | None

    created_at: datetime
    updated_at: datetime

    promise_location: PromiseLocationRead | None
    promise_location_id: UUID4 | None
    admin_user_id: UUID4 | None
    admin_user: UserRead | None
    participants: list["WorkoutParticipantRead"]
    status: WorkoutPromiseStatus

    class Config:
        orm_mode = True


# id -> from path parameter
class WorkoutPromiseUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, min_length=1, max_length=1000)
    is_private: bool = Field(False, description="Is Private workout promise?")

    max_participants: int | None = Field(None, ge=1, le=10)
    promise_time: datetime | None = Field(None, description="Promise datetime")
    recruit_end_time: datetime | None = Field(None, description="Recruit end datetime")
    admin_user_id: UUID4 | None = Field(None, description="New Admin User ID")
    promise_location: PromiseLocationBase | None = Field(None)
    status: WorkoutPromiseStatus | None = Field(None)
    workout_part: str | None = Field(None, description="Workout part")

    def get_update_dict(self):
        return self.dict(
            exclude_unset=True,
            exclude={
                "id",
                "created_at",
                "updated_at",
                "chat_room_id",
                "admin_user_id",
                "promise_location_id",
            },
        )


class WorkoutParticipantBase(BaseModel):
    name: str | None = Field(
        min_length=1,
        max_length=100,
        description="NickName of participant in Promise",
    )
    status: ParticipantStatus = Field(ParticipantStatus.PENDING)
    status_message: str | None = Field(
        None, description="Status message of participant"
    )
    is_admin: bool = Field(False, description="Is admin of Promise")

    class Config:
        orm_mode = True


class WorkoutParticipantRead(WorkoutParticipantBase):
    id: UUID4
    chat_room_member_id: UUID4 | None
    workout_promise_id: UUID4 | None
    created_at: datetime
    updated_at: datetime
    user_id: UUID4 | None
    user: UserRead | None

    class Config:
        orm_mode = True


class WorkoutParticipantUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    status: ParticipantStatus | None = Field(None)
    status_message: str | None = Field(
        None, description="Status message of participant"
    )
    is_admin: bool = Field(False, description="Is admin of Promise")

    def get_update_dict(self):
        return self.dict(
            exclude_unset=True,
            exclude={
                "id",
                "user_id",
                "workout_promise_id",
                "chat_room_member_id",
                "created_at",
                "updated_at",
                "is_admin",
            },
        )


class BaseListResponse(BaseModel):
    total: int | None


class WorkoutPromiseListResponse(BaseListResponse):
    items: list[WorkoutPromiseRead]
    next_cursor: int | None

    class Config:
        orm_mode = True


WorkoutPromiseRead.update_forward_refs()
WorkoutParticipantRead.update_forward_refs()
