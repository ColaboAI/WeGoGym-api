from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


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


class ParticipantStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class WorkoutParticipantBase(BaseModel):
    status: ParticipantStatus
    created_at: datetime
    updated_at: datetime


class WorkoutParticipantCreate(WorkoutParticipantBase):
    pass


class WorkoutParticipantUpdate(WorkoutParticipantBase):
    pass


class WorkoutParticipantRead(WorkoutParticipantBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class WorkoutPromiseBase(BaseModel):
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    created_at: datetime
    updated_at: datetime


class WorkoutPromiseCreate(WorkoutPromiseBase):
    pass


class WorkoutPromiseUpdate(WorkoutPromiseBase):
    pass


class WorkoutPromiseRead(WorkoutPromiseBase):
    id: int
    max_participants: int
    participants: list[WorkoutParticipantRead]

    class Config:
        orm_mode = True
