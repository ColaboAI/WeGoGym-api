import asyncio
from datetime import datetime

from sqlalchemy import func, select, text
from app.models.chat import ChatRoom, ChatRoomMember, Message
from app.models.user import User
from app.utils.ecs_log import logger
import json
from fastapi import HTTPException, WebSocket
from aioredis.client import Redis, PubSub
from app.core.helpers.redis import get_redis_conn
from dataclasses import asdict, dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.guid import GUID
from sqlalchemy.orm import selectinload
from starlette.websockets import WebSocketState


class ChatService:
    def __init__(
        self,
        websocket: WebSocket,
        chat_room_id: GUID,
        user_id: GUID,
        session: AsyncSession,
    ):
        super().__init__()
        self.ws: WebSocket = websocket
        self.chat_room_id = chat_room_id
        self.user_id = user_id
        self.get_redis_conn = get_redis_conn
        self.session = session

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

    async def run(self):
        conn: Redis = await self.get_redis_conn()

        pubsub: PubSub = conn.pubsub()

        tasks = [self.publish_handler(conn), self.subscribe_handler(pubsub)]
        results = await asyncio.gather(*tasks)
        print(f"Done task: {results}")
        logger.info(f"Done task: {results}")


@dataclass(slots=True)
class ChatMessage:
    chat_room_id: GUID
    user_id: GUID
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
    return result.scalars().first()


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


async def get_chat_room_mems_list_by_user_id(
    user_id: int, session: AsyncSession, limit: int, offset: int | None = None
):
    """return all chat room that user is in"""
    stmt = (
        select(ChatRoomMember)
        .order_by(ChatRoomMember.created_at.desc())
        .where(ChatRoomMember.user_id == user_id)
    )
    total = (
        select(func.count(ChatRoomMember.id))
        .select_from(ChatRoomMember)
        .where(ChatRoomMember.user_id == user_id)
    )
    if offset:
        stmt = stmt.offset(offset)
    if limit:
        stmt = stmt.limit(limit)
    total = await session.execute(total)
    result = await session.execute(stmt)
    return total.scalars().first(), result.scalars().all()


# public
async def get_public_chat_room_list(
    session: AsyncSession, limit: int, offset: int | None = None
):
    """return all chat room that user is in"""
    stmt = (
        select(ChatRoom)
        .order_by(ChatRoom.created_at.desc())
        .where(ChatRoom.is_private == False)
    )
    total = (
        select(func.count(ChatRoom.id))
        .select_from(ChatRoom)
        .where(ChatRoom.is_private == False)
    )
    if offset:
        stmt = stmt.offset(offset)
    if limit:
        stmt = stmt.limit(limit)
    total = await session.execute(total)

    result = await session.execute(stmt)
    return total.scalars().first(), result.scalars().all()


async def make_chat_room(user_id: GUID, session: AsyncSession):
    chat_room = ChatRoom(user_id=user_id)
    session.add(chat_room)
    await session.commit()
    return chat_room


async def make_chat_room_member(user_id: GUID, room_id: GUID, session: AsyncSession):
    chat_room_member = ChatRoomMember(user_id=user_id, chat_room_id=room_id)
    session.add(chat_room_member)
    await session.commit()
    return chat_room_member


async def delete_chat_room_member(user_id: GUID, room_id: GUID, session: AsyncSession):
    stmt = text(
        "DELETE FROM chat_room_members WHERE user_id = :user_id AND chat_room_id = :room_id"
    )
    await session.execute(stmt, {"user_id": user_id, "room_id": room_id})
    await session.commit()


async def delete_chat_room(room_id: GUID, session: AsyncSession):
    stmt = text("DELETE FROM chat_rooms WHERE id = :room_id")

    await session.execute(stmt, {"room_id": room_id})
    await session.commit()


async def get_chat_room_members(room_id: GUID, session: AsyncSession):

    stmt = text("SELECT user_id FROM chat_room_members WHERE chat_room_id = :room_id")

    result = await session.execute(stmt, {"room_id": room_id})
    return result.fetchall()


async def get_chat_room_members_count(room_id: GUID, session: AsyncSession):

    stmt = text("SELECT COUNT(*) FROM chat_room_members WHERE chat_room_id = :room_id")

    result = await session.execute(stmt, {"room_id": room_id})
    return result.fetchone()


async def get_user_by_id(user_id: GUID, session: AsyncSession) -> User:
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    return result.fetchone()


async def post_chat_message(
    user_id: GUID, room_id: GUID, message: str, session: AsyncSession
):
    # get user from db
    # user = await get_user_by_id(user_id, session)
    # chat_room = await get_chat_room_by_id(room_id, session)

    msg = Message(user_id=user_id, chat_room_id=room_id, text=message)
    session.add(msg)

    await session.commit()
    return msg


async def get_chat_messages(
    room_id: GUID,
    last_read_at: datetime,
    session: AsyncSession,
    limit: int = 10,
    offset: int | None = None,
):
    stmt = (
        select(Message)
        .where(
            Message.chat_room_id == room_id,
            Message.created_at > last_read_at,
        )
        .order_by(Message.created_at.desc(), Message.id.desc())
    )
    total = select(func.count(Message.id)).where(
        Message.chat_room_id == room_id, Message.created_at > last_read_at
    )
    total = await session.execute(total)
    if offset:
        stmt = stmt.offset(offset)
    if limit:
        stmt = stmt.limit(limit)

    result = await session.execute(stmt)
    return total.scalars().first(), result.scalars().all()


async def update_last_read_at_by_mem_id(
    session: AsyncSession, chat_room_member_id: GUID
):
    stmt = select(ChatRoomMember).where(ChatRoomMember.id == chat_room_member_id)
    result = await session.execute(stmt)
    chat_room_member_obj = result.scalars().first()
    if not chat_room_member_obj:
        raise HTTPException(status_code=404, detail="Chat room member not found")

    chat_room_member_obj.last_read_at = datetime.now()

    await session.commit()


async def delete_chat_room_member_by_id(
    session: AsyncSession, chat_room_member_id: GUID, user_id: GUID
):

    stmt = text(
        "DELETE FROM chat_room_members WHERE id = :chat_room_member_id AND user_id = :user_id"
    )
    await session.execute(
        stmt, {"chat_room_member_id": chat_room_member_id, "user_id": user_id}
    )
    await session.commit()


async def delete_chat_room_member_admin_by_id(
    session: AsyncSession, chat_room_member_id: GUID, admin_id: GUID, chat_room_id: GUID
):

    admin_mem = await get_user_mem_with_ids(admin_id, chat_room_id, session)
    if not admin_mem.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")

    stmt = text("DELETE FROM chat_room_members WHERE id = :chat_room_member_id")
    await session.execute(stmt, {"chat_room_member_id": chat_room_member_id})
    await session.commit()
