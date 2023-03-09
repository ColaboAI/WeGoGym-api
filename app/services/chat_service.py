import asyncio
from datetime import datetime, timezone
from uuid import UUID
from pydantic import UUID4

from sqlalchemy import distinct, false, func, select, text
from app.models.chat import ChatRoom, ChatRoomMember, Message
from app.models.user import User
from app.utils.ecs_log import logger
import json
from fastapi import HTTPException, WebSocket
from aioredis.client import Redis, PubSub
from app.core.helpers.redis import get_redis_conn
from dataclasses import asdict, dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, aliased
from starlette.websockets import WebSocketState


class ChatService:
    def __init__(
        self,
        websocket: WebSocket,
        chat_room_id: str,
        user_id: str,
        session: AsyncSession,
    ):
        super().__init__()
        self.ws: WebSocket = websocket
        self.chat_room_id = chat_room_id
        self.user_id = user_id
        self.get_redis_conn = get_redis_conn
        self.session = session
        self.conn = None

    async def publish_handler(self, conn: Redis):
        try:
            while True:
                if self.ws.application_state == WebSocketState.CONNECTED:

                    message = await self.ws.receive_text()
                    if message:
                        msg = await post_chat_message(
                            self.user_id,
                            self.chat_room_id,
                            message,
                            self.session,
                        )
                        chat_message = ChatMessage(
                            chat_room_id=self.chat_room_id,
                            user_id=self.user_id,
                            text=message,
                            created_at=msg.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        )

                        await conn.publish(
                            self.chat_room_id, json.dumps(asdict(chat_message))
                        )
                else:
                    logger.warning(
                        f"Websocket state: {self.ws.application_state}, reconnecting..."  # noqa: E501
                    )
                    await self.ws.accept()

        except Exception as e:
            logger.debug(e)

    async def subscribe_handler(self, pubsub: PubSub):
        await pubsub.subscribe(self.chat_room_id)
        try:
            while True:
                if self.ws.application_state == WebSocketState.CONNECTED:

                    message = await pubsub.get_message(ignore_subscribe_messages=True)
                    if message:
                        data = json.loads(message.get("data"))
                        chat_message = ChatMessage(**data)
                        await self.ws.send_text(
                            f"[{chat_message.created_at}] {chat_message.text} ({chat_message.user_id})"
                        )
                else:
                    logger.warning(
                        f"Websocket state: {self.ws.application_state}, reconnecting..."  # noqa: E501
                    )
                    await self.ws.accept()
        except Exception as e:
            logger.debug(e)
            await self.ws.close()
            if self.conn:
                await self.conn.close()

    async def run(self):
        conn: Redis = await self.get_redis_conn()
        self.conn = conn
        pubsub: PubSub = conn.pubsub()

        tasks = [self.publish_handler(conn), self.subscribe_handler(pubsub)]
        done, pending = await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED,
        )
        logger.info(f"Done task: {done}")
        for task in pending:
            logger.debug(f"Canceling task: {task}")
            task.cancel()
        for task in done:
            task.result()


@dataclass(slots=True)
class ChatMessage:
    chat_room_id: str
    user_id: str
    created_at: str
    text: str


async def get_user_mem_with_ids(
    user_id: str,
    room_id: str,
    session: AsyncSession,
) -> ChatRoomMember:
    """return chat room member if user is in room"""

    stmt = select(ChatRoomMember).where(
        ChatRoomMember.chat_room_id == room_id, ChatRoomMember.user_id == user_id
    )
    result = await session.execute(stmt)
    data = result.scalars().first()
    if data is None:
        raise HTTPException(status_code=404, detail="User not in room")
    return data


async def get_chat_room_and_members_by_id(chat_room_id: str, session: AsyncSession):
    """return chat room and members by room_id"""
    stmt = (
        select(ChatRoom)
        .options(selectinload(ChatRoom.members))
        .where(ChatRoom.id == chat_room_id)
    )
    result = await session.execute(stmt)
    chat_room = result.scalars().first()
    return chat_room


async def get_chat_room_by_id(chat_room_id: int, session: AsyncSession):
    """return chat room by room_id"""
    stmt = select(ChatRoom).where(ChatRoom.id == chat_room_id)
    result = await session.execute(stmt)
    chat_room = result.scalars().first()
    return chat_room


# TODO
async def get_chat_room_list_by_user_id(
    session: AsyncSession, user_id: int, limit: int, offset: int | None = None
) -> tuple[int | None, list[ChatRoom]]:
    """return all chat room that user is in"""

    chat_rooms = (
        select(ChatRoomMember.chat_room_id, ChatRoomMember.last_read_at)
        .where(ChatRoomMember.user_id == user_id)
        .cte("chat_rooms")
    )

    stmt = (
        select(ChatRoom)
        .options(
            selectinload(ChatRoom.members).options(
                selectinload(ChatRoomMember.user).load_only(
                    User.id, User.username, User.profile_pic
                ),
            )
        )
        .order_by(ChatRoom.created_at.desc())
        .where(ChatRoom.id == chat_rooms.c.chat_room_id)
    )

    last_msg = (
        select(
            Message.chat_room_id,
            Message.text.label("last_message_text"),
            Message.created_at.label("last_message_created_at"),
        )
        .where(Message.chat_room_id == chat_rooms.c.chat_room_id)
        .order_by(Message.created_at.desc())
        .limit(1)
        .cte("last_msg")
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

    stmt = stmt.add_columns(
        last_msg.c.last_message_text, last_msg.c.last_message_created_at
    ).join(last_msg, ChatRoom.id == last_msg.c.chat_room_id, isouter=True)

    stmt = stmt.add_columns(unread_count.c.unread_count).join(
        unread_count, ChatRoom.id == unread_count.c.chat_room_id, isouter=True
    )

    total_stmt = (
        select(func.count(ChatRoomMember.id))
        .select_from(ChatRoomMember)
        .where(ChatRoomMember.user_id == user_id)
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
async def get_public_chat_room_list(
    session: AsyncSession, limit: int, offset: int | None = None
):
    """return all chat room that user is in"""
    stmt = (
        select(ChatRoom)
        .order_by(ChatRoom.created_at.desc())
        .where(ChatRoom.is_private.is_(False))
    )
    total_stmt = (
        select(func.count(ChatRoom.id))
        .select_from(ChatRoom)
        .where(ChatRoom.is_private.is_(False))
    )
    if offset:
        stmt = stmt.offset(offset)
    if limit:
        stmt = stmt.limit(limit)
    total = await session.execute(total_stmt)

    result = await session.execute(stmt)
    return total.scalars().first(), result.scalars().all()


async def make_chat_room_member(user_id: str, room_id: str, session: AsyncSession):
    chat_room_member = ChatRoomMember(user_id=user_id, chat_room_id=room_id)
    session.add(chat_room_member)
    await session.commit()
    return chat_room_member


async def delete_chat_room_member(user_id: str, room_id: str, session: AsyncSession):
    stmt = text(
        "DELETE FROM chat_room_members WHERE user_id = :user_id AND chat_room_id = :room_id"
    )
    await session.execute(stmt, {"user_id": user_id, "room_id": room_id})
    await session.commit()


async def delete_chat_room(room_id: str, session: AsyncSession):
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


async def get_user_by_id(user_id: str, session: AsyncSession) -> User:
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    usr: User | None = result.scalars().first()
    if usr is None:
        raise HTTPException(status_code=404, detail="User not found")
    return usr


async def post_chat_message(
    user_id: str, room_id: str, message: str, session: AsyncSession
):
    # get user from db
    # user = await get_user_by_id(user_id, session)
    # chat_room = await get_chat_room_by_id(room_id, session)

    msg = Message(user_id=user_id, chat_room_id=room_id, text=message)
    session.add(msg)

    await session.commit()
    return msg


async def get_chat_messages(
    session: AsyncSession,
    room_id: str,
    last_read_at: datetime | None = None,
    limit: int = 10,
    offset: int = 0,
):
    # last_read_at = None인 경우는 처음 메시지를 읽는 경우
    stmt = (
        select(Message)
        .where(
            Message.chat_room_id == room_id,
            Message.created_at > last_read_at,
        )
        .order_by(Message.created_at.desc(), Message.id.desc())
    )
    total_stmt = select(func.count(Message.id)).where(
        Message.chat_room_id == room_id, Message.created_at > last_read_at
    )
    total = await session.execute(total_stmt)
    if offset:
        stmt = stmt.offset(offset)
    if limit:
        stmt = stmt.limit(limit)

    result = await session.execute(stmt)
    return total.scalars().first(), result.scalars().all()


async def update_last_read_at_by_mem_id(
    session: AsyncSession, chat_room_member_id: str
):
    stmt = select(ChatRoomMember).where(ChatRoomMember.id == chat_room_member_id)
    result = await session.execute(stmt)
    chat_room_member_obj = result.scalars().first()
    if not chat_room_member_obj:
        raise HTTPException(status_code=404, detail="Chat room member not found")

    chat_room_member_obj.last_read_at = datetime.now(timezone.utc)

    await session.commit()


async def delete_chat_room_member_by_id(
    session: AsyncSession, chat_room_member_id: str, user_id: str
):

    stmt = text(
        "DELETE FROM chat_room_members WHERE id = :chat_room_member_id AND user_id = :user_id"
    )
    await session.execute(
        stmt, {"chat_room_member_id": chat_room_member_id, "user_id": user_id}
    )
    await session.commit()


async def delete_chat_room_member_admin_by_id(
    session: AsyncSession, chat_room_member_id: str, admin_id: str, chat_room_id: str
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


async def get_last_message_and_members_by_room_id(
    session: AsyncSession, room_id: UUID
) -> Message | None:
    stmt = (
        select(Message)
        .where(Message.chat_room_id == room_id)
        .order_by(Message.created_at.desc(), Message.id.desc())
        .limit(1)
    )

    result = await session.execute(stmt)
    msg = result.scalars().first()
    return msg


async def find_direct_chat_room_by_user_ids(
    session: AsyncSession, user_ids: list[UUID4]
):
    stmt = (
        select(
            ChatRoom.id,
        )
        .join(ChatRoomMember, ChatRoom.id == ChatRoomMember.chat_room_id)
        .where(
            (ChatRoom.is_group_chat.is_(False)) & (ChatRoomMember.user_id.in_(user_ids))
        )
        .group_by(ChatRoom.id)
        .having(func.count(distinct(ChatRoomMember.user_id)) == len(user_ids))
    )
    res = await session.execute(stmt)
    rows = res.fetchone()
    if not rows:
        return None

    chat_room = await get_chat_room_and_members_by_id(rows[0], session)
    return chat_room
