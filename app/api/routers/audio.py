from fastapi import APIRouter, Depends

from app.api.deps import get_current_active_user

audio_router = APIRouter()


@audio_router.get("/audio")
async def authenticated_route(user: UserRead = Depends(get_current_active_user)):
    return {"message": f"Hello {user.email}!"}
