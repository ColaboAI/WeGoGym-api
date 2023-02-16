from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.db.mixins.timestamp_mixin import TimestampMixin
from app.models.base import Base
from app.models.guid import GUID
from app.schemas import ParticipantStatus


class WorkoutPromise(TimestampMixin, Base):
    __tablename__ = "workout_promise"
    __mapper_args__ = {"eager_defaults": True}
    id = Column(GUID, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    max_participants = Column(Integer, default=3)
    participants = relationship(
        "WorkoutParticipant",
        back_populates="workout_promise",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )


class WorkoutParticipant(TimestampMixin, Base):
    __tablename__ = "workout_participant"
    __mapper_args__ = {"eager_defaults": True}
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    workout_promise_id = Column(
        Integer, ForeignKey("workout_promise.id", ondelete="SET NULL")
    )
    workout_promise = relationship("WorkoutPromise", back_populates="participants")
    status = Column(String, default=ParticipantStatus.PENDING, index=True)
