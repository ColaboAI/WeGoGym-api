from datetime import datetime, timezone

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import insert, select, update
from app.core.exceptions.chat import ChatRoomNotFound
from app.core.fastapi.dependencies.premission import (
    IsAuthenticated,
    PermissionDependency,
)
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
    get_chat_room_by_id,
    get_chat_room_list_by_user_id,
    get_chat_room_member_by_user_and_room_id,
    get_public_chat_room_list,
    get_user_by_id,
    get_user_mem_with_ids,
    make_chat_room_member,
)
from app.services.workout_promise_service import get_workout_promise_by_id, get_workout_promise_with_participants
from app.session import get_db_transactional_session
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.helpers.cache import Cache

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
@Cache.cached(ttl=60)
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
        chat_room.members_user_ids,
        chat_room.is_group_chat,
    )

    if db_chat_room:
        if chat_room.is_group_chat == False:
            raise HTTPException(status_code=409, detail="Chat room already exists")

    try:
        chat_room_obj = await session.scalar(
            insert(ChatRoom)
            .values(**chat_room.model_dump(exclude={"members_user_ids", "retry", "workout_promise_id"}))
            .returning(ChatRoom)
        )
        if chat_room_obj is None:
            raise HTTPException(status_code=400, detail="Failed to create chat room")

        chat_mems = (
            await session.scalars(
                insert(ChatRoomMember)
                .values(
                    [
                        {
                            "user_id": uid,
                            "chat_room_id": chat_room_obj.id,
                            "is_admin": False if uid != chat_room.admin_user_id else True,
                        }
                        for uid in chat_room.members_user_ids
                    ]
                )
                .returning(ChatRoomMember)
            )
        ).all()

        if chat_room.workout_promise_id:
            workout_promise = await get_workout_promise_with_participants(session, chat_room.workout_promise_id)
            workout_promise.chat_room_id = chat_room_obj.id
            for wpp in workout_promise.participants:
                if wpp.user_id in chat_room.members_user_ids:
                    wpp.chat_room_member_id = next(filter(lambda x: x.user_id == wpp.user_id, chat_mems)).id
            session.add(workout_promise)

        await session.commit()

        return await get_chat_room_and_members_by_id(chat_room_obj.id, session)
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


@chat_router.get("/rooms/{chat_room_id}/members", response_model=list[ChatRoomMemberRead])
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

    t, res = await get_chat_messages(session, chat_room_id, chat_room_member.created_at, limit, offset)

    chat_room_member.last_read_at = datetime.now(timezone.utc)
    await session.commit()
    return {
        "total": t,
        "items": res,
        "next_cursor": offset + len(res) if t and t > offset + len(res) else None,
    }


@chat_router.post(
    "/room/{chat_room_id}/user/{user_id}",
    response_model=ChatRoomMemberRead,
    status_code=201,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    summary="Add chat room member(Not Admin)",
)
async def add_chat_room_member(
    chat_room_id: UUID,
    user_id: UUID,
    session: AsyncSession = Depends(get_db_transactional_session),
):
    chat_room = await get_chat_room_by_id(chat_room_id, session)
    if chat_room is None:
        raise ChatRoomNotFound

    db_chat_mem = await get_chat_room_member_by_user_and_room_id(user_id, chat_room_id, session)
    if db_chat_mem:
        raise HTTPException(status_code=409, detail="Chat room member already exists")

    try:
        chat_room_member = await make_chat_room_member(user_id, chat_room_id, session)
        return chat_room_member
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


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
    await delete_chat_room_member_by_user_and_room_id(session=session, user_id=user_id, room_id=chat_room_id)


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
    await delete_chat_room_member_admin_by_id(session, chat_room_member_id, request.user.id, chat_room_id)


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
    if chat_room is None:
        raise ChatRoomNotFound
    return chat_room
