from typing import TYPE_CHECKING
import uuid
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
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
    __tablename__ = "workout_promise"
    __mapper_args__ = {"eager_defaults": True}
    id = Column(GUID, primary_key=True, index=True, default=uuid.uuid4)
    title = Column(String, index=True, nullable=False)
    description = Column(String, index=True, nullable=False)
    max_participants = Column(Integer, default=3, nullable=False)
    is_private = Column(Boolean, default=False)
    status = Column(
        String,
        default=WorkoutPromiseStatus.RECRUITING,
        server_default=WorkoutPromiseStatus.RECRUITING,
        index=True,
        nullable=False,
    )
    recruit_end_time = Column(DateTime(timezone=True), index=True)
    # TODO: workout_id and related table should be added
    promise_time = Column(DateTime(timezone=True), index=True, server_default=utcnow())
    workout_part = Column(String, index=True, nullable=True)
    # Child table (One to "Many")
    admin_user_id = Column(
        GUID,
        ForeignKey("user.id", ondelete="CASCADE"),
    )
    admin_user: "User" = relationship(
        "User", back_populates="admin_workout_promises", lazy="select"
    )

    # 1:1 relationship
    chat_room_id = Column(GUID, ForeignKey("chat_room.id", ondelete="SET NULL"))
    chat_room: "ChatRoom" = relationship(
        "ChatRoom", back_populates="workout_promise", lazy="select"
    )

    gym_info_id = Column(GUID, ForeignKey("gym_info.id", ondelete="SET NULL"))
    gym_info: "GymInfo" = relationship(
        "GymInfo", back_populates="workout_promises", lazy="select"
    )
    # Parent relationship (Many to "One")
    participants: list["WorkoutParticipant"] = relationship(
        "WorkoutParticipant",
        back_populates="workout_promise",
        cascade="save-update, merge, delete",
        passive_deletes=True,
        lazy="select",
    )


class WorkoutParticipant(TimestampMixin, Base):
    __tablename__ = "workout_participant"
    __mapper_args__ = {"eager_defaults": True}
    id = Column(GUID, primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, index=True)

    # 참여 여부, 승인 여부
    status = Column(String, default=ParticipantStatus.PENDING, index=True)

    # 참여신청 시, 상태메세지를 입력할 수 있음
    # 참여 후에는 상태메세지로 참여자의 운동 등의 상태를 알 수 있음
    status_message = Column(String)
    is_admin = Column(Boolean, default=False, nullable=False)

    # ("Many" to one)
    user_id = Column(GUID, ForeignKey("user.id", ondelete="CASCADE"))
    user: "User" = relationship("User", back_populates="workout_participants")

    # ("Many" to one)
    workout_promise_id = Column(
        GUID, ForeignKey("workout_promise.id", ondelete="CASCADE")
    )
    workout_promise: WorkoutPromise = relationship(
        "WorkoutPromise", back_populates="participants"
    )

    # 1:1 relationship child
    chat_room_member_id = Column(
        GUID, ForeignKey("chat_room_member.id", ondelete="SET NULL")
    )
    chat_room_member: "ChatRoomMember" = relationship(
        "ChatRoomMember", back_populates="workout_participant"
    )

    notifications_workout_sender: list["NotificationWorkout"] = relationship(
        "NotificationWorkout",
        back_populates="sender",
        cascade="save-update, merge, delete",
        passive_deletes=True,
        foreign_keys="NotificationWorkout.sender_id",
    )

    notifications_workout_recipient: list["NotificationWorkout"] = relationship(
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
    __tablename__ = "gym_info"
    __mapper_args__ = {"eager_defaults": True}
    id = Column(GUID, primary_key=True, index=True, default=uuid.uuid4)
    # 헬스장 이름
    name = Column(String, index=True, nullable=False)
    # 사용자가 직접 등록한 헬스장인지 여부
    is_custom_gym = Column(Boolean, default=False)
    # 도로명 주소
    address = Column(String, index=True, nullable=False, unique=True)
    # 우편번호
    zip_code = Column(String)
    # 영업 상태
    status = Column(String)

    # (Many to "one") with workout_promise
    workout_promises: list[WorkoutPromise] = relationship(
        "WorkoutPromise",
        back_populates="gym_info",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )

    # Parent relationship (Many to "One")
    users: list["User"] = relationship(
        "User",
        back_populates="gym_info",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )
    # (Many to Many, 삭제시 cascade 안함.)
    facilities: list["GymFacility"] = relationship(
        "GymFacility",
        secondary=gym_info_facility_association,
        back_populates="gym_infos",
    )


class GymFacility(Base):
    __tablename__ = "gym_facility"
    id = Column(GUID, primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False, unique=True)
    description = Column(String, index=True)

    # (Many to Many)
    gym_infos: list[GymInfo] = relationship(
        "GymInfo",
        secondary=gym_info_facility_association,
        back_populates="facilities",
    )


# class Workout(TimestampMixin, Base):
#     __tablename__ = "workout"
#     __mapper_args__ = {"eager_defaults": True}
#     id = Column(GUID, primary_key=True, index=True, default=uuid.uuid4)
#     name = Column(String, index=True, nullable=False)
#     description = Column(String, index=True)
#     category = Column(String, index=True, nullable=False)
#     difficulty = Column(String, index=True, nullable=False)
#     equipment = Column(String, index=True, nullable=False)
#     muscle_group = Column(String, index=True, nullable=False)
#     duration = Column(Integer, index=True, nullable=False)
#     calories = Column(Integer, index=True, nullable=False)
#     video_url = Column(String, index=True, nullable=False)
#     thumbnail_url = Column(String, index=True, nullable=False)
#     is_public = Column(Boolean, default=False, index=True)
