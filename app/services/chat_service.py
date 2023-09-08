import asyncio
from datetime import datetime, timezone
from uuid import UUID
from fastapi.websockets import WebSocketState

from sqlalchemy import delete, distinct, func, select, text
from app.core.exceptions.chat import (
    ChatMemberNotFound,
    ChatRoomNotFound,
    UserNotInChatRoom,
)
from app.models.chat import ChatRoom, ChatRoomMember, Message
from app.models.user import User, user_block_list
from app.services.fcm_service import send_message_to_multiple_devices_by_fcm_token_list
from app.services.user_service import get_blocked_me_list
from app.utils.ecs_log import logger
import ujson
from fastapi import HTTPException, WebSocket, WebSocketDisconnect

from coredis import RedisCluster
from coredis.commands import ShardedPubSub
from app.core.helpers.redis import chat_redis as redis
from dataclasses import asdict, dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.exc import NoResultFound
from app.core.conn import conn_manager


# TODO: When Keyboard interrupt, close the connection. and task must be cancelled
class ChatService:
    def __init__(
        self,
        websocket: WebSocket,
        chat_room_id: UUID,
        user_id: UUID,
        session: AsyncSession,
    ):
        super().__init__()
        self.ws: WebSocket = websocket
        self.chat_room_id = chat_room_id
        self.user_id = user_id
        self.session = session
        self.conn: RedisCluster = redis
        self.pubsub: ShardedPubSub | None = None

    async def publish_handler(self, conn: RedisCluster):
        while True:
            try:
                if self.ws.client_state == WebSocketState.CONNECTED:
                    m = await self.ws.receive_text()
                    message: dict = ujson.loads(m)

                    if message:
                        text = message["text"]
                        msg = await post_chat_message(
                            self.user_id,
                            self.chat_room_id,
                            text,
                            self.session,
                        )

                        msg_data = ChatMessageDataClass(
                            id=msg.id.__str__(),
                            text=msg.text.__str__(),
                            created_at=msg.created_at.__str__(),
                            user_id=msg.user_id.__str__(),
                            chat_room_id=msg.chat_room_id.__str__(),
                            type="text_message",
                        )

                        await conn.spublish(
                            self.chat_room_id.__str__(),
                            ujson.dumps(asdict(msg_data)),
                        )

                        banned_set = await get_blocked_me_list(
                            self.session,
                            self.user_id,
                        )
                        banned_set.add(self.user_id)

                        db_chat_room = await get_chat_room_and_members_by_id(self.chat_room_id, self.session)

                        fcm_tokens = [
                            member.user.fcm_token
                            for member in db_chat_room.members
                            if member.user.fcm_token and member.user.id not in banned_set
                        ]
                        title = msg.user.username
                        body = msg.text

                        await send_message_to_multiple_devices_by_fcm_token_list(
                            fcm_tokens, title, body, data=asdict(msg_data)
                        )
                    else:
                        logger.warning("Websocket Connection State Changed")
                        break

            except Exception as e:
                e.args += ("ChatService subscribe_handler",)
                raise e

    async def subscribe_handler(self, pubsub: ShardedPubSub):
        await pubsub.subscribe(self.chat_room_id.__str__())
        while True:
            # FIXME: asyncio gather로 묶어서 task cancel이 안되는 문제가 있음
            try:
                message = await pubsub.get_message()
                if message and message.get("type") == "message":
                    data_in_message = message.get("data", None)
                    if isinstance((data_in_message), str) and data_in_message:
                        data = ujson.loads(data_in_message)
                        chat_message = ChatMessageDataClass(**data)
                        await self.ws.send_json(asdict(chat_message), mode="text")
            except asyncio.CancelledError as e:
                logger.debug(f"Subscribe handler cancelled: {e}")
                await pubsub.unsubscribe(self.chat_room_id.__str__())
                raise e

            except Exception as e:
                e.args += ("ChatService subscribe_handler",)
                raise e

    async def run(self):
        self.pubsub: ShardedPubSub = self.conn.sharded_pubsub()
        task_1 = asyncio.create_task(self.publish_handler(self.conn))
        task_2 = asyncio.create_task(self.subscribe_handler(self.pubsub))
        tasks = [task_1, task_2]
        try:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

            for task in pending:
                logger.debug(f"Cancel task: {task}")
                task.cancel()
            for task in done:
                logger.debug(f"Result: {task.result()}")
                raise task.exception()

        except Exception as e:
            logger.debug(f"Run exception: {e}")
            raise e
        finally:
            if self.pubsub:
                await self.pubsub.close()
                del self.pubsub
            if self.ws:
                del self.ws


@dataclass(slots=True)
class ChatMessageDataClass:
    id: str
    type: str
    chat_room_id: str
    user_id: str
    created_at: str
    text: str = "text"


async def get_user_mem_with_ids(
    user_id: UUID,
    room_id: UUID,
    session: AsyncSession,
) -> ChatRoomMember:
    """return chat room member if user is in room"""

    stmt = select(ChatRoomMember).where(ChatRoomMember.chat_room_id == room_id, ChatRoomMember.user_id == user_id)
    result = await session.execute(stmt)
    data = result.scalars().first()
    if data is None:
        raise UserNotInChatRoom
    return data


async def get_chat_room_and_members_by_id(chat_room_id: UUID, session: AsyncSession) -> ChatRoom:
    """return chat room and members by room_id"""
    stmt = (
        select(ChatRoom)
        .options(
            selectinload(ChatRoom.members).options(
                selectinload(ChatRoomMember.user).load_only(
                    User.id,
                    User.username,
                    User.profile_pic,
                    User.fcm_token,
                )
            )
        )
        .where(ChatRoom.id == chat_room_id)
    )

    try:
        result = await session.execute(stmt)
        chat_room = result.scalars().first()
        if chat_room is None:
            raise ChatRoomNotFound
        return chat_room
    except NoResultFound:
        raise ChatRoomNotFound


async def get_chat_room_by_id(chat_room_id: UUID, session: AsyncSession):
    """return chat room by room_id"""
    stmt = select(ChatRoom).where(ChatRoom.id == chat_room_id)
    result = await session.execute(stmt)
    chat_room = result.scalars().first()
    return chat_room


# TODO
async def get_chat_room_list_by_user_id(
    session: AsyncSession, user_id: UUID, limit: int, offset: int | None = None
) -> tuple[int | None, list[ChatRoom]]:
    """return all chat room that user is in"""

    chat_rooms = (
        select(ChatRoomMember.chat_room_id, ChatRoomMember.last_read_at)
        .where(ChatRoomMember.user_id == user_id)
        .cte("chat_rooms")
    )

    last_msg_created_time = (
        select(
            Message.chat_room_id,
            func.max(Message.created_at).label("last_message_created_at"),
        )
        .where(
            Message.chat_room_id == chat_rooms.c.chat_room_id,
        )
        .group_by(Message.chat_room_id)
        .subquery()
    )
    last_msg = (
        select(
            Message.text.label("last_message_text"),
            Message.created_at.label("last_message_created_at"),
            Message.chat_room_id,
        )
        .where(
            Message.chat_room_id == last_msg_created_time.c.chat_room_id,
            Message.created_at == last_msg_created_time.c.last_message_created_at,
        )
        .subquery()
    )

    stmt = (
        select(ChatRoom)
        .options(
            selectinload(ChatRoom.members).options(
                selectinload(ChatRoomMember.user).load_only(User.id, User.username, User.profile_pic),
            )
        )
        .join(
            last_msg,
            ChatRoom.id == last_msg.c.chat_room_id,
            isouter=True,
        )
        .add_columns(last_msg.c.last_message_text, last_msg.c.last_message_created_at)
        .order_by(last_msg.c.last_message_created_at.desc())
        .where(
            ChatRoom.id == chat_rooms.c.chat_room_id,
            ChatRoom.admin_user_id.notin_(
                select(user_block_list.c.blocked_user_id).where(user_block_list.c.user_id == user_id)
            ),
        )
    )

    unread_count = (
        select(
            Message.chat_room_id,
            func.count("*").label("unread_count"),
        )
        .where(
            Message.chat_room_id == chat_rooms.c.chat_room_id,
            Message.created_at > chat_rooms.c.last_read_at,
        )
        .group_by(Message.chat_room_id)
        .cte("unread_count")
    )

    stmt = stmt.add_columns(unread_count.c.unread_count).join(
        unread_count, ChatRoom.id == unread_count.c.chat_room_id, isouter=True
    )

    total_stmt = (
        select(func.count(ChatRoomMember.id))
        .select_from(ChatRoomMember)
        .join(
            ChatRoom,
            ChatRoomMember.chat_room_id == ChatRoom.id,
        )
        .where(
            ChatRoomMember.user_id == user_id,
            ChatRoom.admin_user_id.notin_(
                select(user_block_list.c.blocked_user_id).where(user_block_list.c.user_id == user_id)
            ),
        )
    )

    if offset:
        stmt = stmt.offset(offset)
    if limit:
        stmt = stmt.limit(limit)

    total = await session.execute(total_stmt)
    result = await session.execute(stmt)

    out = []
    for row in result:
        row.ChatRoom.last_message_text = row.last_message_text
        row.ChatRoom.last_message_created_at = row.last_message_created_at
        row.ChatRoom.unread_count = row.unread_count
        out.append(row.ChatRoom)

    return total.scalars().first(), out


# public
async def get_public_chat_room_list(session: AsyncSession, limit: int, offset: int | None = None):
    """return all chat room that user is in"""
    stmt = select(ChatRoom).order_by(ChatRoom.created_at.desc()).where(ChatRoom.is_private.is_(False))
    total_stmt = select(func.count(ChatRoom.id)).select_from(ChatRoom).where(ChatRoom.is_private.is_(False))
    if offset:
        stmt = stmt.offset(offset)
    if limit:
        stmt = stmt.limit(limit)
    total = await session.execute(total_stmt)

    result = await session.execute(stmt)
    return total.scalars().first(), result.scalars().all()


async def get_chat_room_member_by_user_and_room_id(
    user_id: UUID,
    room_id: UUID,
    session: AsyncSession,
):
    stmt = select(ChatRoomMember).where(ChatRoomMember.user_id == user_id, ChatRoomMember.chat_room_id == room_id)
    result = await session.execute(stmt)
    chat_room_member = result.scalars().first()
    return chat_room_member


async def make_chat_room_member(user_id: UUID, room_id: UUID, session: AsyncSession):
    chat_room_member = ChatRoomMember(user_id=user_id, chat_room_id=room_id)  # type: ignore
    session.add(chat_room_member)
    await session.commit()
    return chat_room_member


async def delete_chat_room_member_by_user_and_room_id(
    session: AsyncSession,
    user_id: UUID,
    room_id: UUID,
):
    stmt = text("DELETE FROM chat_room_member WHERE user_id = :user_id AND chat_room_id = :room_id")
    try:
        await session.execute(stmt, {"user_id": user_id, "room_id": room_id})
        await session.commit()
    except Exception as e:
        logger.debug(f"Chat mem delete failed: {e}")
        raise ChatMemberNotFound


async def delete_chat_room_by_id(room_id: str, session: AsyncSession):
    stmt = text("DELETE FROM chat_rooms WHERE id = :room_id")

    await session.execute(stmt, {"room_id": room_id})
    await session.commit()


async def get_chat_room_members(room_id: str, session: AsyncSession):
    stmt = text("SELECT user_id FROM chat_room_members WHERE chat_room_id = :room_id")

    result = await session.execute(stmt, {"room_id": room_id})
    return result.fetchall()


async def get_chat_room_members_count(room_id: str, session: AsyncSession):
    stmt = text("SELECT COUNT(*) FROM chat_room_members WHERE chat_room_id = :room_id")

    result = await session.execute(stmt, {"room_id": room_id})
    return result.fetchone()


async def get_user_by_id(user_id: UUID, session: AsyncSession) -> User:
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    usr: User | None = result.scalars().first()
    if usr is None:
        raise HTTPException(status_code=404, detail="User not found")
    return usr


async def post_chat_message(user_id: UUID, room_id: UUID, message: str, session: AsyncSession):
    msg = Message(user_id=user_id, chat_room_id=room_id, text=message)  # type: ignore
    session.add(msg)

    await session.commit()
    return msg


async def get_chat_messages(
    session: AsyncSession,
    room_id: UUID,
    created_at: datetime | None = None,
    limit: int = 10,
    offset: int = 0,
):
    # last_read_at = None인 경우는 처음 메시지를 읽는 경우
    stmt = (
        select(Message)
        .where(
            Message.chat_room_id == room_id,
            Message.created_at > created_at,
        )
        .order_by(Message.created_at.desc(), Message.id.desc())
    )
    total_stmt = select(func.count(Message.id)).where(Message.chat_room_id == room_id, Message.created_at > created_at)
    total = await session.execute(total_stmt)
    if offset:
        stmt = stmt.offset(offset)
    if limit:
        stmt = stmt.limit(limit)

    result = await session.execute(stmt)
    return total.scalars().first(), result.scalars().all()


async def update_last_read_at_by_mem_id(session: AsyncSession, chat_room_member_id: str):
    stmt = select(ChatRoomMember).where(ChatRoomMember.id == chat_room_member_id)
    result = await session.execute(stmt)
    chat_room_member_obj = result.scalars().first()
    if not chat_room_member_obj:
        raise HTTPException(status_code=404, detail="Chat room member not found")

    chat_room_member_obj.last_read_at = datetime.now(timezone.utc)

    await session.commit()


async def delete_chat_room_member_by_id(session: AsyncSession, chat_room_member_id: str, user_id: str):
    # stmt = text(
    #     "DELETE FROM chat_room_members WHERE id = :chat_room_member_id AND user_id = :user_id"
    # )
    # await session.execute(
    #     stmt, {"chat_room_member_id": chat_room_member_id, "user_id": user_id}
    # )
    # await session.commit()
    stmt = delete(ChatRoomMember).where(ChatRoomMember.id == chat_room_member_id, ChatRoomMember.user_id == user_id)
    try:
        await session.execute(stmt)
        await session.commit()
    except NoResultFound:
        raise ChatMemberNotFound


async def delete_chat_room_member_admin_by_id(
    session: AsyncSession, chat_room_member_id: UUID, admin_id: UUID, chat_room_id: UUID
):
    admin_mem = await get_user_mem_with_ids(admin_id, chat_room_id, session)
    if not admin_mem.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")

    stmt = text("DELETE FROM chat_room_members WHERE id = :chat_room_member_id")
    await session.execute(stmt, {"chat_room_member_id": chat_room_member_id})
    await session.commit()


async def get_chat_message_by_id(session: AsyncSession, message_id: UUID) -> Message:
    stmt = select(Message).where(Message.id == message_id)
    result = await session.execute(stmt)
    msg = result.scalars().first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    return msg


async def get_last_message_and_members_by_room_id(session: AsyncSession, room_id: UUID) -> Message | None:
    stmt = (
        select(Message)
        .where(Message.chat_room_id == room_id)
        .order_by(Message.created_at.desc(), Message.id.desc())
        .limit(1)
    )

    result = await session.execute(stmt)
    msg = result.scalars().first()
    return msg


async def find_chat_room_by_user_ids(
    session: AsyncSession,
    user_ids: list[UUID],
    is_group_chat: bool = False,
):
    stmt = (
        select(
            ChatRoom.id,
        )
        .join(ChatRoomMember, ChatRoom.id == ChatRoomMember.chat_room_id)
        .where((ChatRoom.is_group_chat.is_(is_group_chat)) & (ChatRoomMember.user_id.in_(user_ids)))
        .group_by(ChatRoom.id)
        .having(func.count(distinct(ChatRoomMember.user_id)) == len(user_ids))
    )
    res = await session.execute(stmt)
    row = res.fetchone()

    if not row:
        return None

    chat_room = await get_chat_room_and_members_by_id(row[0], session)
    return chat_room
