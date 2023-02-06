from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declared_attr

from app.utils.generics import utcnow


class TimestampMixin:
    @declared_attr
    def created_at(cls):
        return Column(DateTime, server_default=utcnow(), nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime,
            server_default=utcnow(),
            onupdate=utcnow(),
            nullable=False,
        )
