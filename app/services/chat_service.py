import asyncio

from sqlalchemy import select, text
from app.models.chat import ChatRoom, ChatRoomMember
from app.utils.ecs_log import logger
from datetime import datetime
import json
from fastapi import WebSocket
from aioredis.client import Redis, PubSub
from app.core.helpers.redis import get_redis_conn
from dataclasses import asdict, dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.guid import GUID


class ChatService:
    def __init__(self, websocket: WebSocket, chat_room_id: GUID, user_id: GUID):
        super().__init__()
        self.ws: WebSocket = websocket
        self.chat_room_id = chat_room_id
        self.user_id = user_id
        self.get_redis_conn = get_redis_conn

    async def publish_handler(self, conn: Redis):
        try:
            while True:
                message = await self.ws.receive_text()
                if message:
                    now = datetime.now()
                    date_time = now.strftime("%Y-%m-%d %H:%M:%S")
                    chat_message = ChatMessage(
                        chat_room_id=self.chat_room_id,
                        user_id=self.user_id,
                        created_at=date_time,
                        text=message,
                    )

                    await conn.publish(
                        self.chat_room_id, json.dumps(asdict(chat_message))
                    )

        except Exception as e:
            logger.debug(e)

    async def subscribe_handler(self, pubsub: PubSub):
        await pubsub.subscribe(self.chat_room_id)
        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    data = json.loads(message.get("data"))
                    chat_message = ChatMessage(**data)
                    await self.ws.send_text(
                        f"[{chat_message.created_at}] {chat_message.text} ({chat_message.user_id})"
                    )
        except Exception as e:
            logger.debug(e)

    async def run(self):
        conn: Redis = await self.get_redis_conn()

        pubsub: PubSub = conn.pubsub()

        tasks = [self.publish_handler(conn), self.subscribe_handler(pubsub)]
        results = await asyncio.gather(*tasks)

        logger.info(f"Done task: {results}")


@dataclass(slots=True)
class ChatMessage:
    chat_room_id: GUID
    user_id: GUID
    created_at: str
    text: str


async def find_existed_user_in_room(
    user_id: int,
    room_id: int,
    session: AsyncSession,
):
    """return chat room member if user is in room"""

    stmt = select(ChatRoomMember).where(
        ChatRoomMember.chat_room_id == room_id, ChatRoomMember.user_id == user_id
    )
    result = await session.execute(stmt)
    return result.fetchone()


async def find_chat_room_by_id(room_id: int, session: AsyncSession):
    """return chat room by room_id"""
    stmt = select(ChatRoom).where(ChatRoom.id == room_id)
    result = await session.execute(stmt)
    return result.fetchone()


async def find_chat_room_by_user_id(user_id: int, session: AsyncSession):
    """return all chat room that user is in"""
    stmt = select(ChatRoomMember).where(ChatRoomMember.user_id == user_id)
    result = await session.execute(stmt)
    return result.fetchall()


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


async def post_chat_message(
    user_id: GUID, room_id: GUID, message: str, session: AsyncSession
):
    stmt = text(
        "INSERT INTO chat_messages (user_id, chat_room_id, text) VALUES (:user_id, :room_id, :message)"
    )
    await session.execute(
        stmt, {"user_id": user_id, "room_id": room_id, "message": message}
    )
    await session.commit()
