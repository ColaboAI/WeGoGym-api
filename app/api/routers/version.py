from fastapi import APIRouter
from app.schemas.version import latest_version

version_router = APIRouter()


# 앱 버전 정보 가져오기
@version_router.get(
    "/",
    summary="Get app version",
    description="Get app version",
)
async def get_app_version():
    return latest_version
