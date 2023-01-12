from fastapi import APIRouter

from app.api.routers.audio import audio_router


api_router = APIRouter()

api_router.include_router(
    audio_router,
    prefix="/audio",
    tags=["audio"],
)
