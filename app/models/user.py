"""
SQL Alchemy models declaration.

Note, imported by alembic migrations logic, see `alembic/env.py`
"""

from typing import Union
from fastapi_users.db import (
    SQLAlchemyBaseOAuthAccountTableUUID,
    SQLAlchemyBaseUserTableUUID,
)
from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import relationship

from app.models import Base


class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    pass


# @declarative_mixin
class User(SQLAlchemyBaseUserTableUUID, Base):

    oauth_accounts: list[OAuthAccount] = relationship("OAuthAccount", lazy="joined")
    username: str = Column(String(100), nullable=False)
    phone_number: str = Column(String(100), nullable=False)
    profile_pic: Union[str, None] = Column(String(100))
    bio: Union[str, None] = Column(String(100))
    age: Union[int, None] = Column(Integer)
    weight: Union[int, None] = Column(Integer)
    longitude: Union[float, None] = Column(Float)
    latitude: Union[float, None] = Column(Float)
    last_active_at: Union[int, None] = Column(Integer)
    workout_per_week: Union[int, None] = Column(Integer)
