import uuid
import firebase_admin
from firebase_admin import messaging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

default_app = firebase_admin.initialize_app(
    credential=firebase_admin.credentials.Certificate("firebase.json")
)


async def subscribe_fcm_token_to_topic(
    db: AsyncSession, user_id: uuid.UUID, topic: str
):
    from app.models.user import User

    user = await db.get(User, user_id)

    if user is None or user.fcm_token is None:
        return

    try:
        response = messaging.subscribe_to_topic(user.fcm_token, topic)
        print("Successfully subscribed to topic:", response)
    except Exception as e:
        print("Error subscribing to topic:", e)


# google fcm admin sdk 를 사용하여 메시지를 보내는 함수
async def send_message_to_single_device(
    db: AsyncSession,
    user_id: uuid.UUID,
    title: str,
    body: str,
    data: dict[str, str] | None = None,
):
    user = await db.get(User, user_id)

    if user is None or user.fcm_token is None:
        return

    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=user.fcm_token,
        data=data,
    )
    try:
        response = messaging.send(message)
        print("Successfully sent message:", response)
    except Exception as e:
        print("Error sending message:", e)


# multiple device 에 메시지를 보내는 함수
async def send_message_to_multiple_devices_by_uid_list(
    db: AsyncSession,
    user_ids: list[uuid.UUID],
    title: str,
    body: str,
    data: dict[str, str] | None = None,
):
    users = await db.execute(select().where(User.id.in_(user_ids)))
    tokens = [user.fcm_token for user in users if user.fcm_token is not None]

    if len(tokens) == 0:
        return

    message = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=body),
        tokens=tokens,
        data=data,
    )
    try:
        response = messaging.send_multicast(message)
        print("Successfully sent message:", response)
    except Exception as e:
        print("Error sending message:", e)


async def send_message_to_multiple_devices_by_fcm_token_list(
    tokens: list[str],
    title: str,
    body: str,
    data: dict[str, str] | None = None,
):
    if len(tokens) == 0:
        return

    message = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=body),
        tokens=tokens,
        data=data,
    )
    try:
        response = messaging.send_multicast(message)
        print("Successfully sent message:", response)
    except Exception as e:
        print("Error sending message:", e)


# topic 으로 메시지를 보내는 함수
async def send_message_to_topic(
    topic: str, title: str, body: str, data: dict[str, str] | None = None
):
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        topic=topic,
        data=data,
    )
    try:
        response = messaging.send(message)
        print("Successfully sent message:", response)
    except Exception as e:
        print("Error sending message:", e)
