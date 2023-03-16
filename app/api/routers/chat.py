from datetime import datetime, timezone

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import select
from app.core.fastapi.dependencies.premission import (
    IsAuthenticated,
    PermissionDependency,
)
from app.models.user import User
from app.schemas.chat import (
    ChatRoomList,
    ChatRoomCreate,
    ChatRoomMemberRead,
    ChatRoomWithMembersRead,
    MessageListRead,
    MyChatRoomList,
)
from app.models.chat import ChatRoom, ChatRoomMember
from app.services.chat_service import (
    delete_chat_room_member_admin_by_id,
    delete_chat_room_member_by_user_and_room_id,
    find_chat_room_by_user_ids,
    get_chat_messages,
    get_chat_room_and_members_by_id,
    get_chat_room_list_by_user_id,
    get_public_chat_room_list,
    get_user_mem_with_ids,
)
from app.session import get_db_transactional_session
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.generics import utcnow


chat_router = APIRouter()


# TODO: handle error with custom exception
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
    return {"total": t, "items": r}


# Private chat rooms (user's chat rooms)
@chat_router.get(
    "/rooms/me",
    response_model=MyChatRoomList,
    summary="My chat rooms member list with limits",
    description="Get My chat rooms from latest to oldest",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def get_my_chat_rooms(
    request: Request,
    session: AsyncSession = Depends(get_db_transactional_session),
    limit: int = Query(10, description="Limit"),
    offset: int = Query(None, description="offset"),
):
    t, c = await get_chat_room_list_by_user_id(session, request.user.id, limit, offset)

    return {
        "total": t,
        "items": c,
        "next_cursor": offset + len(c) if t and t > offset + len(c) else None,
    }


@chat_router.post("/rooms", response_model=ChatRoomWithMembersRead, status_code=201)
async def create_chat_room(
    chat_room: ChatRoomCreate,
    session: AsyncSession = Depends(get_db_transactional_session),
):
    db_chat_room = await find_chat_room_by_user_ids(
        session,
        [chat_room.created_by, *chat_room.members_user_ids],
        chat_room.is_group_chat,
    )
    if db_chat_room:
        if chat_room.is_group_chat == False:
            raise HTTPException(status_code=409, detail="Chat room already exists")
        else:
            if chat_room.retry == False:
                raise HTTPException(
                    status_code=409,
                    detail="Chat room already exists with same members. If you want to create new chat room with same members please change the name of the chat room and try again",
                )

    try:
        chat_room_obj = ChatRoom(
            **chat_room.dict(exclude={"members_user_ids", "retry"})
        )
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

        if chat_room.is_group_chat == True:
            for id in chat_room.members_user_ids:
                res = await session.execute(select(User).where(User.id == id))
                user = res.scalars().first()
                if not user:
                    raise HTTPException(status_code=404, detail="User not found")
                chat_room_member_obj = ChatRoomMember(
                    user=user,
                    chat_room=chat_room_obj,
                    is_admin=False,
                )
                # TODO: Watchout for this, it might be a bug.
                # duplicated members are added to the chat room.(only response)
                chat_room_obj.members.append(chat_room_member_obj)

        else:
            if len(chat_room.members_user_ids) != 1:
                raise HTTPException(
                    status_code=400, detail="Invalid Request For Direct Chat Room"
                )
            res = await session.execute(
                select(User).where(User.id == chat_room.members_user_ids[0])
            )
            user = res.scalars().first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            chat_room_member_obj = ChatRoomMember(
                user=user, chat_room=chat_room_obj, is_admin=True
            )

        session.add(chat_room_obj)

        await session.commit()

        return chat_room_obj
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.get("/rooms/{chat_room_id}", response_model=ChatRoomWithMembersRead)
async def get_chat_room(
    chat_room_id: UUID,
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
    chat_room_id: UUID,
    session: AsyncSession = Depends(get_db_transactional_session),
):
    stmt = select(ChatRoomMember).where(ChatRoomMember.chat_room_id == chat_room_id)
    result = await session.execute(stmt)
    return result.scalars().all()


@chat_router.get(
    "/rooms/{chat_room_id}/messages",
    response_model=MessageListRead,
    summary="Get chat room messages",
    description="Get chat room messages from latest to oldest by chat room id and last read time",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def get_chat_room_messages(
    req: Request,
    chat_room_id: UUID,
    limit: int = Query(10, description="Limit"),
    offset: int = Query(0, description="Offset"),
    session: AsyncSession = Depends(get_db_transactional_session),
):
    chat_room_member = await get_user_mem_with_ids(req.user.id, chat_room_id, session)
    if not chat_room_member:
        raise HTTPException(status_code=403, detail="User is not in the room")

    t, res = await get_chat_messages(
        session, chat_room_id, chat_room_member.created_at, limit, offset
    )

    chat_room_member.last_read_at = datetime.now(timezone.utc)
    await session.commit()
    return {
        "total": t,
        "items": res,
        "next_cursor": offset + len(res) if t and t > offset + len(res) else None,
    }


@chat_router.delete(
    "/room/{chat_room_id}/user/{user_id}",
    status_code=204,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def delete_chat_room_member_by_uid(
    request: Request,
    chat_room_id: UUID,
    user_id: UUID,
    session: AsyncSession = Depends(get_db_transactional_session),
):
    if request.user.id != user_id:
        raise HTTPException(status_code=403, detail="User is not allowed to do this")
    await delete_chat_room_member_by_user_and_room_id(
        session=session, user_id=user_id, room_id=chat_room_id
    )


@chat_router.delete(
    "room/{chat_room_id}/{chat_room_member_id}/admin",
    status_code=204,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def delete_chat_room_member_admin(
    request: Request,
    chat_room_id: UUID,
    chat_room_member_id: UUID,
    session: AsyncSession = Depends(get_db_transactional_session),
):
    await delete_chat_room_member_admin_by_id(
        session, chat_room_member_id, request.user.id, chat_room_id
    )


@chat_router.get(
    "/room/direct",
    response_model=ChatRoomWithMembersRead,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def get_direct_chat_room_by_user_ids(
    req: Request,
    user_ids: list[UUID] = Query(..., description="User ids"),
    session: AsyncSession = Depends(get_db_transactional_session),
):
    user_ids.append(req.user.id)
    chat_room = await find_chat_room_by_user_ids(session, user_ids, is_group_chat=False)
    return chat_room
