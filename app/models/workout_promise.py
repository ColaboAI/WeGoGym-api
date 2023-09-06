from datetime import datetime
from typing import TYPE_CHECKING
import uuid
from pydantic import UUID4
from sqlalchemy import (
    Column,
    Float,
    String,
    DateTime,
    Integer,
    ForeignKey,
    Boolean,
    Table,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.db.mixins.timestamp_mixin import TimestampMixin
from app.models.base import Base
from app.models.guid import GUID
from app.schemas import ParticipantStatus
from app.schemas.workout_promise import WorkoutPromiseStatus
from app.utils.generics import utcnow

if TYPE_CHECKING:
    # if the target of the relationship is in another module
    # that cannot normally be imported at runtime
    from . import ChatRoom, User, ChatRoomMember, NotificationWorkout


class WorkoutPromise(TimestampMixin, Base):
    __mapper_args__ = {"eager_defaults": True}
    id: Mapped[UUID4] = mapped_column(GUID, primary_key=True, index=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String, index=True, nullable=False)
    max_participants: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(
        String,
        default=WorkoutPromiseStatus.RECRUITING,
        server_default=WorkoutPromiseStatus.RECRUITING,
        index=True,
        nullable=False,
    )
    recruit_end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    # TODO: workout_id and related table should be added
    promise_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, server_default=utcnow(), nullable=False
    )
    workout_part: Mapped[str] = mapped_column(String, index=True, nullable=True)
    # Child table (One to "Many")
    admin_user_id: Mapped[UUID4] = mapped_column(
        GUID,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    admin_user: Mapped["User"] = relationship("User", back_populates="admin_workout_promises", lazy="select")

    # 1:1 relationship
    chat_room_id: Mapped[UUID4] = mapped_column(GUID, ForeignKey("chat_room.id", ondelete="SET NULL"), nullable=True)
    chat_room: Mapped["ChatRoom"] = relationship("ChatRoom", back_populates="workout_promise", lazy="select")

    promise_location_id: Mapped[UUID4] = mapped_column(
        GUID, ForeignKey("promise_location.id", ondelete="SET NULL"), nullable=True
    )
    promise_location: Mapped["PromiseLocation"] = relationship(
        "PromiseLocation", back_populates="workout_promises", lazy="select"
    )
    # Parent relationship (Many to "One")
    participants: Mapped[list["WorkoutParticipant"]] = relationship(
        "WorkoutParticipant",
        back_populates="workout_promise",
        cascade="save-update, merge, delete",
        passive_deletes=True,
        lazy="select",
    )


class WorkoutParticipant(TimestampMixin, Base):
    __mapper_args__ = {"eager_defaults": True}
    id: Mapped[UUID4] = mapped_column(GUID, primary_key=True, index=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, index=True, nullable=True)

    # 참여 여부, 승인 여부
    status: Mapped[str] = mapped_column(String, default=ParticipantStatus.PENDING, index=True, nullable=False)

    # 참여신청 시, 상태메세지를 입력할 수 있음
    # 참여 후에는 상태메세지로 참여자의 운동 등의 상태를 알 수 있음
    status_message: Mapped[str] = mapped_column(String, nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ("Many" to one)
    user_id: Mapped[UUID4] = mapped_column(GUID, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="workout_participants")

    # ("Many" to one)
    workout_promise_id: Mapped[UUID4] = mapped_column(
        GUID, ForeignKey("workout_promise.id", ondelete="CASCADE"), nullable=False
    )
    workout_promise: Mapped[WorkoutPromise] = relationship("WorkoutPromise", back_populates="participants")

    # 1:1 relationship child
    chat_room_member_id: Mapped[UUID4] = mapped_column(
        GUID, ForeignKey("chat_room_member.id", ondelete="SET NULL"), nullable=True
    )
    chat_room_member: Mapped["ChatRoomMember"] = relationship("ChatRoomMember", back_populates="workout_participant")

    notifications_workout_sender: Mapped[list["NotificationWorkout"]] = relationship(
        "NotificationWorkout",
        back_populates="sender",
        cascade="save-update, merge, delete",
        passive_deletes=True,
        foreign_keys="NotificationWorkout.sender_id",
    )

    notifications_workout_recipient: Mapped[list["NotificationWorkout"]] = relationship(
        "NotificationWorkout",
        back_populates="recipient",
        cascade="save-update, merge, delete",
        passive_deletes=True,
        foreign_keys="NotificationWorkout.recipient_id",
    )


# Many to Many
# TODO: 하나가 지워지면 다른 하나도 지워지지 않도록 수정
gym_info_facility_association = Table(
    "gym_info_facility_association_table",
    Base.metadata,
    Column(
        "gym_info_id",
        GUID,
        ForeignKey("gym_info.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "facility_id",
        GUID,
        ForeignKey("gym_facility.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class GymInfo(TimestampMixin, Base):  # type: ignore
    __mapper_args__ = {"eager_defaults": True}
    id: Mapped[UUID4] = mapped_column(GUID, primary_key=True, index=True, default=uuid.uuid4)
    # 헬스장 이름
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    # 사용자가 직접 등록한 헬스장인지 여부
    is_custom_gym: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # 도로명 주소
    address: Mapped[str] = mapped_column(String, index=True, nullable=False, unique=True)
    # 우편번호
    zip_code: Mapped[str] = mapped_column(String, nullable=True)
    # 영업 상태
    status: Mapped[str] = mapped_column(String, nullable=True)

    # Parent relationship (Many to "One")
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="gym_info",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )
    # (Many to Many, 삭제시 cascade 안함.)
    facilities: Mapped[list["GymFacility"]] = relationship(
        "GymFacility",
        secondary=gym_info_facility_association,
        back_populates="gym_infos",
    )


class GymFacility(Base):
    id: Mapped[UUID4] = mapped_column(GUID, primary_key=True, index=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String, index=True, nullable=True)

    # (Many to Many)
    gym_infos: Mapped[list[GymInfo]] = relationship(
        "GymInfo",
        secondary=gym_info_facility_association,
        back_populates="facilities",
    )


class PromiseLocation(TimestampMixin, Base):
    __mapper_args__ = {"eager_defaults": True}
    id: Mapped[UUID4] = mapped_column(GUID, primary_key=True, index=True, default=uuid.uuid4)
    # 장소 이름
    place_name: Mapped[str] = mapped_column(String, nullable=False)
    # 위도
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    # 경도
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    # 주소
    address: Mapped[str] = mapped_column(String, nullable=False)

    workout_promises: Mapped[list[WorkoutPromise]] = relationship(
        "WorkoutPromise",
        back_populates="promise_location",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )
