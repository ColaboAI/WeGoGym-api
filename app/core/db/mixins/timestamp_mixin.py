from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declared_attr, declarative_mixin

from app.utils.generics import utcnow


@declarative_mixin
class TimestampMixin:
    @declared_attr
    def created_at(cls) -> Column[DateTime]:
        return Column(DateTime(timezone=True), server_default=utcnow(), nullable=False)

    @declared_attr
    def updated_at(cls) -> Column[DateTime]:
        return Column(
            DateTime(timezone=True),
            server_default=utcnow(),
            onupdate=utcnow(),
            nullable=False,
        )
