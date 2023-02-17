from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field
from app.schemas.chat import ChatRoomMemberRead, ChatRoomRead


class ParticipantStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class GymInfoBase(BaseModel):
    name: str
    address: str
    zip_code: str | None
    status: str | None


class GymInfoRead(GymInfoBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UpdateDictModel(BaseModel):
    def get_update_dict(self):
        return self.dict(
            exclude_unset=True,
            exclude={
                "id",
                "created_at",
                "updated_at",
                "user_id",
                "workout_promise_id",
                "chat_room_member_id",
                "status",
                "is_admin",
            },
        )


class WorkoutParticipantUpdate(UpdateDictModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    status: ParticipantStatus | None = Field(None)
    status_message: str | None = Field(
        None,
    )


class WorkoutPromiseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)
    is_private: bool = Field(False, description="Is Private workout promise?")
    max_participants: int = Field(..., ge=1, le=10)
    promise_time: datetime = Field(...)
    recruit_end_time: datetime | None = Field(None, description="Recruit end time")
    admin_user_id: UUID = Field(..., description="Admin User ID")


class WorkoutPromiseRead(WorkoutPromiseBase):
    id: UUID
    chat_room_id: UUID | None
    chat_room: ChatRoomRead | None

    participants: list["WorkoutParticipantRead"]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# id -> from path parameter
class WorkoutPromiseUpdate(WorkoutPromiseBase):
    title: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, min_length=1, max_length=1000)

    max_participants: int | None = Field(None, ge=1, le=10)
    promise_time: datetime | None = Field(None, description="Promise datetime")
    recruit_end_time: datetime | None = Field(None, description="Recruit end datetime")


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

    user_id: UUID = Field(..., description="User ID of participant")
    workout_promise_id: UUID = Field(..., description="Workout Promise ID")


class WorkoutParticipantRead(WorkoutParticipantBase):
    id: UUID
    chat_room_member_id: UUID | None

    created_at: datetime
    updated_at: datetime

    # workout_promise: WorkoutPromiseRead
    # chat_room_member: ChatRoomMemberRead

    class Config:
        orm_mode = True


class WorkoutParticipantUpdate(WorkoutParticipantBase):
    status: ParticipantStatus | None = Field(None)
    status_message: str | None = Field(
        None, description="Status message of participant"
    )

    user_id: None = None
    workout_promise_id: None = None


WorkoutPromiseRead.update_forward_refs()
