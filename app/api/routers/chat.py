# create chat room
# create chat room member
# create chat message는 필요할까

# Path: app/api/routers/chat.py
# Compare this snippet from app/api/router/audio.py:
# from fastapi import APIRouter, Depends, UploadFile, Form, HTTPException
# from botocore.exceptions import ClientError
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.utils.ecs_log import logger


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from app.models.user import User
from app.schemas import user
from app.schemas.chat import (
    ChatRoomRead,
    ChatRoomCreate,
    ChatRoomMemberRead,
    MessageRead,
)
from app.models.chat import ChatRoom, ChatRoomMember, Message
from app.session import get_db_transactional_session
from sqlalchemy.ext.asyncio import AsyncSession


chat_router = APIRouter()


@chat_router.get("/rooms", response_model=list[ChatRoomRead])
async def get_chat_rooms(session: AsyncSession = Depends(get_db_transactional_session)):
    stmt = select(ChatRoom)
    result = await session.execute(stmt)
    return result.scalars().all()


@chat_router.post("/rooms", response_model=ChatRoomRead, status_code=201)
async def create_chat_room(
    chat_room: ChatRoomCreate,
    session: AsyncSession = Depends(get_db_transactional_session),
):
    try:
        chat_room_obj = ChatRoom(**chat_room.dict(exclude={"members_user_id"}))

        stmt = select(User).where(User.id == chat_room.created_by)
        admin_user = await session.execute(stmt)
        admin_user = admin_user.scalars().first()

        if not admin_user:
            raise HTTPException(status_code=404, detail="Room Admin User is not found")

        admin_member_obj = ChatRoomMember(
            user=admin_user,
            chat_room=chat_room_obj,
            is_admin=True,
        )
        chat_room_obj.members.append(admin_member_obj)

        for id in chat_room.members_user_id:
            user = await session.execute(select(User).where(User.id == id))
            user = user.scalars().first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            chat_room_member_obj = ChatRoomMember(
                user=user,
                chat_room=chat_room_obj,
            )
            chat_room_obj.members.append(chat_room_member_obj)
        session.add(chat_room_obj)

        await session.commit()

        print(
            "chat_room_obj", chat_room_obj.__dict__, chat_room_obj.members[0].__dict__
        )
        return chat_room_obj
    except Exception as e:
        await session.rollback()
        print("error", e)
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.get("/rooms/{chat_room_id}", response_model=ChatRoomRead)
async def get_chat_room(
    chat_room_id: str,
    session: AsyncSession = Depends(get_db_transactional_session),
):
    stmt = select(ChatRoom).where(ChatRoom.id == chat_room_id)
    result = await session.execute(stmt)
    chat_room = result.scalars().first()
    if chat_room is None:
        raise HTTPException(status_code=404, detail="Chat room not found")
    return chat_room


@chat_router.get(
    "/rooms/{chat_room_id}/members", response_model=list[ChatRoomMemberRead]
)
async def get_chat_room_members(
    chat_room_id: str,
    session: AsyncSession = Depends(get_db_transactional_session),
):
    stmt = select(ChatRoomMember).where(ChatRoomMember.chat_room_id == chat_room_id)
    result = await session.execute(stmt)
    return result.scalars().all()


@chat_router.get("/rooms/{chat_room_id}/messages", response_model=list[MessageRead])
async def get_chat_room_messages(
    chat_room_id: str,
    user_id: str,
    session: AsyncSession = Depends(get_db_transactional_session),
):
    get_chat_room_members_stmt = select(ChatRoomMember).where(
        ChatRoomMember.chat_room_id == chat_room_id, ChatRoomMember.user_id == user_id
    )
    chat_mem_result = await session.execute(get_chat_room_members_stmt)

    chat_mem: ChatRoomMember = chat_mem_result.fetchone()
    if chat_mem is None:
        raise HTTPException(status_code=404, detail="Chat room not found")

    msg_stmt = select(Message).where(
        Message.chat_room_id == chat_room_id, Message.created_at > chat_mem.last_read_at
    )

    result = await session.execute(msg_stmt)
    return result.scalars().all()
