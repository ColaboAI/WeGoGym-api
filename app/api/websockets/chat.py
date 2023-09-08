from datetime import datetime, timezone
from uuid import UUID
from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
)
from app.core.exceptions.chat import UserNotInChatRoom
from app.core.exceptions.websocket import WSUserNotInChatRoom
from app.utils.ecs_log import logger

from app.session import get_db_transactional_session
from app.services.chat_service import ChatService, get_user_mem_with_ids
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.conn import conn_manager

chat_ws_router = APIRouter(
    prefix="/api/v1/ws/chat",
)


# TODO: Do we need to add a dependency to check if user is in chat room?
# TODO: How to check user auth in websocket?
# 일단은 헤더에 정보를 담을 수 없고, 쿼리 파라미터에 정보를 담을 수 없음.. FastAPI 자체 오류로 추정. 2023.03.15 해결 실패
# 1. JWT token for websocket(small size)
@chat_ws_router.websocket(
    "/{chat_room_id}/{user_id}",
)
async def chat_websocket_endpoint(
    websocket: WebSocket,
    chat_room_id: UUID,
    user_id: UUID,
    session: AsyncSession = Depends(get_db_transactional_session),
):
    try:
        chat_room_member = await get_user_mem_with_ids(user_id, chat_room_id, session)
        str_chat_room_id = chat_room_id.__str__()
        str_user_id = user_id.__str__()

        await conn_manager.connect(str_chat_room_id + str_user_id, websocket)
        chat_service = ChatService(websocket, chat_room_id, user_id, session=session)
        await chat_service.run()
    except UserNotInChatRoom as e:
        raise WSUserNotInChatRoom
    except WebSocketDisconnect as e:
        await conn_manager.disconnect(str_chat_room_id + str_user_id)
    except Exception as e:
        logger.debug(e)
    finally:
        await conn_manager.disconnect(str_chat_room_id + str_user_id)
        chat_room_member.last_read_at = datetime.now(timezone.utc)
        del chat_service
