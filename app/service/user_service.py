# Path: app/service/user_service.py

from fastapi import Depends, HTTPException
from app.models.user import User
from app.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession


async def get_current_user(
    # TODO: use token dependency
    token: str,
    session: AsyncSession = Depends(get_async_session),
):
    user = await session.get(User, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user
