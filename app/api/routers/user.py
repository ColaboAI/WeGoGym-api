from fastapi import APIRouter, Depends

from app.schemas.user import UserRead
from app.api.deps import get_current_active_user

user_router = APIRouter()


@user_router.get("/authenticated-route")
async def authenticated_route(user: UserRead = Depends(get_current_active_user)):
    return {"message": f"Hello {user.email}!"}
