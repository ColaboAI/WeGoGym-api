"""
SQL Alchemy models declaration.

Note, imported by alembic migrations logic, see `alembic/env.py`
"""

from fastapi_users.db import (
    SQLAlchemyBaseOAuthAccountTableUUID,
    SQLAlchemyBaseUserTableUUID,
)
from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import relationship

# from app.models import Base
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta

UserBase: DeclarativeMeta = declarative_base()


class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, UserBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, UserBase):
    oauth_accounts: list[OAuthAccount] = relationship("OAuthAccount", lazy="joined")
    username: Column(String(100), nullable=False)
    phone_number: Column(String(100), nullable=False)
    profile_pic: Column(String(100))
    bio: Column(String(100))
    age: Column(Integer)
    weight: Column(Integer)
    longitude: Column(Float)
    latitude: Column(Float)
    last_active_at: Column(Integer)
    workout_per_week: Column(Integer)
    # TODO: Add relations
