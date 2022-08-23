"""
All fields in schemas are defaults from FastAPI Users, repeated below for easier view
"""

import uuid
from typing import Optional

from fastapi_users import schemas
from pydantic import EmailStr


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass
    # email: EmailStr
    # is_active: bool = True
    # is_superuser: bool = False
    # is_verified: bool = False
    # hashed_password: Optional[str]


class UserCreate(schemas.BaseUserCreate):
    pass
    # email: EmailStr
    # password: str
    # is_active: Optional[bool] = True
    # is_superuser: Optional[bool] = False
    # is_verified: Optional[bool] = False


class UserUpdate(schemas.BaseUserUpdate):
    pass
    # password: Optional[str]
    # email: Optional[EmailStr]
    # is_active: Optional[bool]
    # is_superuser: Optional[bool]
    # is_verified: Optional[bool]
