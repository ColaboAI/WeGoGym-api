from fastapi import APIRouter, Depends, UploadFile, Form, HTTPException, WebSocket
from app.models.chat import ChatRoom
from app.schemas.chat import ChatRoomRead

from app.session import get_db_transactional_session
from app.services.chat_service import ChatService, find_chat_room_by_id
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
    chat_room = await find_chat_room_by_id(chat_room_id, session)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")

    # chat_room_member = chat_room.members.filter_by(user_id=user_id).first()
    # check user is in chat room

    await conn_manager.connect(websocket)
    chat_service = ChatService(websocket, chat_room_id, user_id)
    await chat_service.run()
