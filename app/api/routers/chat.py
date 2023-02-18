# create chat room
# create chat room member
# create chat message는 필요할까

# Path: app/api/routers/chat.py
# Compare this snippet from app/api/router/audio.py:
# from fastapi import APIRouter, Depends, UploadFile, Form, HTTPException
# from botocore.exceptions import ClientError
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.utils.ecs_log import logger


from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from app.core.fastapi.dependencies.premission import (
    IsAuthenticated,
    PermissionDependency,
)
from app.models.user import User
from app.schemas.chat import (
    ChatRoomList,
    ChatRoomMemberList,
    ChatRoomRead,
    ChatRoomCreate,
    ChatRoomMemberRead,
    ChatRoomWithMembersRead,
    MessateListRead,
)
from app.models.chat import ChatRoom, ChatRoomMember
from app.services.chat_service import (
    delete_chat_room_member_admin_by_id,
    delete_chat_room_member_by_id,
    get_chat_messages,
    get_chat_room_and_members_by_id,
    get_chat_room_mems_list_by_user_id,
    get_public_chat_room_list,
    get_user_mem_with_ids,
    update_last_read_at_by_mem_id,
)
from app.session import get_db_transactional_session
from sqlalchemy.ext.asyncio import AsyncSession


chat_router = APIRouter()

# Public chat rooms
@chat_router.get(
    "/rooms",
    response_model=ChatRoomList,
    summary="Get chat room list with limits",
    description="Get chat rooms from latest to oldest",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def get_public_chat_rooms(
    session: AsyncSession = Depends(get_db_transactional_session),
    limit: int = Query(10, description="Limit"),
    offset: int = Query(None, description="offset"),
):
    # TODO: count
    t, r = await get_public_chat_room_list(session, limit, offset)
    return {"total": t, "rooms": r}


# Private chat rooms (user's chat rooms)
@chat_router.get(
    "/rooms/me",
    response_model=ChatRoomMemberList,
    summary="My chat rooms",
    description="Get My chat rooms from latest to oldest",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def get_my_chat_room_members(
    request: Request,
    session: AsyncSession = Depends(get_db_transactional_session),
    limit: int = Query(10, description="Limit"),
    offset: int = Query(None, description="offset"),
):
    t, m = await get_chat_room_mems_list_by_user_id(
        request.user.id, session, limit, offset
    )
    return {"total": t, "members": m}


@chat_router.post("/rooms", response_model=ChatRoomRead, status_code=201)
async def create_chat_room(
    chat_room: ChatRoomCreate,
    session: AsyncSession = Depends(get_db_transactional_session),
):
    try:
        chat_room_obj = ChatRoom(**chat_room.dict(exclude={"members_user_id"}))

        stmt = select(User).where(User.id == chat_room.created_by)
        res = await session.execute(stmt)
        admin_user = res.scalars().first()

        if not admin_user:
            raise HTTPException(status_code=404, detail="Room Admin User is not found")

        admin_member_obj = ChatRoomMember(
            user=admin_user,
            chat_room=chat_room_obj,
            is_admin=True,
        )
        chat_room_obj.members.append(admin_member_obj)

        for id in chat_room.members_user_id:
            res = await session.execute(select(User).where(User.id == id))
            user = res.scalars().first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            chat_room_member_obj = ChatRoomMember(
                user=user,
                chat_room=chat_room_obj,
            )
            chat_room_obj.members.append(chat_room_member_obj)
        session.add(chat_room_obj)

        await session.commit()

        return chat_room_obj
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.get("/rooms/{chat_room_id}", response_model=ChatRoomWithMembersRead)
async def get_chat_room(
    chat_room_id: str,
    session: AsyncSession = Depends(get_db_transactional_session),
):
    chat_room = await get_chat_room_and_members_by_id(chat_room_id, session)
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


@chat_router.get(
    "/rooms/{chat_room_id}/messages",
    response_model=MessateListRead,
    summary="Get chat room messages",
    description="Get chat room messages from latest to oldest by chat room id and last read time",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def get_chat_room_messages(
    req: Request,
    chat_room_id: str,
    limit: int = Query(10, description="Limit"),
    offset: int | None = Query(None, description="Offset"),
    session: AsyncSession = Depends(get_db_transactional_session),
):
    chat_room_member = await get_user_mem_with_ids(req.user.id, chat_room_id, session)
    if not chat_room_member:
        raise HTTPException(status_code=403, detail="User is not in the room")

    t, res = await get_chat_messages(
        session, chat_room_id, chat_room_member.last_read_at, limit, offset
    )

    return {"total": t, "messages": res}


@chat_router.put(
    "/members/{chat_room_member_id}/last_read_at",
    response_model=ChatRoomMemberRead,
    status_code=200,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def update_chat_room_member_last_read_at(
    chat_room_member_id: str,
    session: AsyncSession = Depends(get_db_transactional_session),
):
    return await update_last_read_at_by_mem_id(session, chat_room_member_id)


@chat_router.delete(
    "members/{chat_room_member_id}",
    status_code=204,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def delete_chat_room_member(
    request: Request,
    chat_room_member_id: str,
    session: AsyncSession = Depends(get_db_transactional_session),
):
    await delete_chat_room_member_by_id(session, chat_room_member_id, request.user.id)


@chat_router.delete(
    "room/{chat_room_id}/{chat_room_member_id}/admin",
    status_code=204,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def delete_chat_room_member_admin(
    request: Request,
    chat_room_id: str,
    chat_room_member_id: str,
    session: AsyncSession = Depends(get_db_transactional_session),
):
    await delete_chat_room_member_admin_by_id(
        session, chat_room_member_id, request.user.id, chat_room_id
    )
