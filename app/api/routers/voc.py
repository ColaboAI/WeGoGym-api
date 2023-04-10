from email import message
from fastapi import APIRouter, BackgroundTasks, Depends, Request
from app.core.fastapi.dependencies.premission import (
    IsAuthenticated,
    PermissionDependency,
)
from app.schemas.voc import VOCRequest

from app.utils.voc import create_voc


voc_router = APIRouter()


# 고객의 소리 Global API
@voc_router.post(
    "/global",
    status_code=201,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def create_voc_user(req: Request, bg: BackgroundTasks, body: VOCRequest):
    if body.plaintiff is None:
        body.plaintiff = req.user.id
    bg.add_task(
        create_voc,
        {
            "content": body.__str__(),
        },
    )
    return {"message": "success"}
