import uuid
import firebase_admin
from firebase_admin import messaging
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import NotificationWorkout
from app.models.user import User
from app.utils.ecs_log import logger
from app.schemas.notification import NotificationWorkoutTitle

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


async def send_message_to_single_device_by_fcm_token(
    fcm_token: str,
    title: str,
    body: str,
    data: dict[str, str] | None = None,
):
    apns = messaging.APNSConfig(
        headers={"apns-priority": "10"},
        payload=messaging.APNSPayload(
            aps=messaging.Aps(
                sound="default",
                content_available=True,
                category="mark-as-read",
            ),
        ),
    )

    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=fcm_token,
        data=data,
        apns=apns,
    )
    try:
        response = messaging.send(message)
        logger.debug(f"Successfully sent message: {response}")
    except Exception as e:
        logger.debug(f"Error sending message: {e}")


# google fcm admin sdk 를 사용하여 메시지를 보내는 함수
async def send_message_to_single_device_by_uid(
    db: AsyncSession,
    user_id: UUID4,
    title: str,
    body: str,
    data: dict[str, str] | None = None,
):
    user = await db.get(User, user_id)

    if user is None or user.fcm_token is None:
        return

    apns = messaging.APNSConfig(
        headers={"apns-priority": "10"},
        payload=messaging.APNSPayload(
            aps=messaging.Aps(
                sound="default",
                content_available=True,
                category="mark-as-read",
            ),
        ),
    )

    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=user.fcm_token,
        data=data,
        apns=apns,
    )
    try:
        response = messaging.send(message)
        logger.debug(f"Successfully sent message: {response}")
    except Exception as e:
        logger.debug(f"Error sending message: {e}")


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

    apns = messaging.APNSConfig(
        headers={"apns-priority": "10"},
        payload=messaging.APNSPayload(
            aps=messaging.Aps(
                sound="default",
                content_available=True,
                category="mark-as-read",
            ),
        ),
    )

    message = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=body),
        tokens=tokens,
        data=data,
        apns=apns,
    )
    try:
        response = messaging.send_multicast(message)
        logger.debug(f"Successfully sent message: {response}")
    except Exception as e:
        logger.debug(f"Error sending message: {e}")


async def send_message_to_multiple_devices_by_fcm_token_list(
    tokens: list[str],
    title: str,
    body: str,
    data: dict[str, str] | None = None,
):
    if len(tokens) == 0:
        return

    apns = messaging.APNSConfig(
        headers={"apns-priority": "10"},
        payload=messaging.APNSPayload(
            aps=messaging.Aps(
                sound="default",
                content_available=True,
                category="mark-as-read",
            ),
        ),
    )

    message = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=body),
        tokens=tokens,
        data=data,
        apns=apns,
    )
    try:
        response = messaging.send_multicast(message)
        logger.debug(f"Successfully sent message: {response}")
    except Exception as e:
        logger.debug(f"Error sending message: {e}")


# topic 으로 메시지를 보내는 함수
async def send_message_to_topic(
    topic: str, title: str, body: str, data: dict[str, str] | None = None
):
    apns = messaging.APNSConfig(
        headers={"apns-priority": "10"},
        payload=messaging.APNSPayload(
            aps=messaging.Aps(
                sound="default",
                content_available=True,
                category="mark-as-read",
            ),
        ),
    )

    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        topic=topic,
        data=data,
        apns=apns,
    )
    try:
        response = messaging.send(message)
        logger.debug(f"Successfully sent message: {response}")
    except Exception as e:
        logger.debug(f"Error sending message: {e}")


async def send_notification_workout(
    db: AsyncSession,
    noti_workout: NotificationWorkout,
):
    key: str | None = noti_workout.notification_type
    uid = noti_workout.recipient.user_id
    if key is None or uid is None:
        return
    title: str = NotificationWorkoutTitle[key]
    body = f"{noti_workout.sender.name}: {noti_workout.message}"

    if noti_workout.message is None:
        body = ""
    await send_message_to_single_device_by_uid(
        db,
        uid,
        title,
        body,
    )
