from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, Form, HTTPException, WebSocket
from app.models.chat import ChatRoom, ChatRoomMember
from app.schemas.chat import ChatRoomRead

from app.session import get_db_transactional_session
from app.services.chat_service import ChatService, get_user_mem_with_ids
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.conn import conn_manager
from sqlalchemy import select

chat_ws_router = APIRouter(
    prefix="/ws/chat",
)


@chat_ws_router.websocket("/{chat_room_id}/{user_id}")
async def chat_websocket_endpoint(
    websocket: WebSocket,
    chat_room_id: str,
    user_id: str,
    session: AsyncSession = Depends(get_db_transactional_session),
):
    chat_room_member = await get_user_mem_with_ids(user_id, chat_room_id, session)

    if not chat_room_member:
        raise HTTPException(status_code=403, detail="User is not in the room")

    await conn_manager.connect(websocket)
    chat_service = ChatService(websocket, chat_room_id, user_id, session=session)
    await chat_service.run()
    await conn_manager.disconnect(websocket)
