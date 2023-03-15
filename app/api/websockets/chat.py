import asyncio
from asyncio.log import logger
from datetime import datetime, timezone
from uuid import UUID
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from app.utils.ecs_log import logger

from app.session import get_db_transactional_session
from app.services.chat_service import ChatService, get_user_mem_with_ids
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.conn import conn_manager

chat_ws_router = APIRouter(
    prefix="/api/v1/ws/chat",
)


@chat_ws_router.websocket(
    "/{chat_room_id}/{user_id}",
)
async def chat_websocket_endpoint(
    websocket: WebSocket,
    chat_room_id: UUID,
    user_id: UUID,
    # token: str = Query(..., description="JWT token"),
    session: AsyncSession = Depends(get_db_transactional_session),
):
    # Check user auth with jwt token
    # if not await conn_manager.validate_user(user_id, token):
    #     raise HTTPException(status_code=403, detail="Not authenticated")
    try:
        chat_room_member = await get_user_mem_with_ids(user_id, chat_room_id, session)
        if not chat_room_member:
            raise HTTPException(status_code=403, detail="User is not in the room")
        str_chat_room_id = chat_room_id.__str__()
        str_user_id = user_id.__str__()

        await conn_manager.connect(str_chat_room_id + str_user_id, websocket)
        chat_service = ChatService(websocket, chat_room_id, user_id, session=session)
        await chat_service.run()
    except WebSocketDisconnect:
        await conn_manager.disconnect(str_chat_room_id + "," + str_user_id)
    except Exception as e:
        logger.debug(e)
    finally:
        await conn_manager.disconnect(str_chat_room_id + "," + str_user_id)
        chat_room_member.last_read_at = datetime.now(timezone.utc)
        del chat_service
