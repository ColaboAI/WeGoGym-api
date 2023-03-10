from uuid import UUID
from fastapi import WebSocket
import jwt
from app.core.exceptions.token import DecodeTokenException, ExpiredTokenException

from app.utils.token_helper import TokenHelper

# Add connection manager method to validate user auth
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def validate_user(self, user_id: UUID, token: str):
        # token is jwt token
        if not token:
            return False
        try:
            payload = TokenHelper.decode(
                token,
            )
            user_id_from_token: UUID | None = payload.get("user_id")
        except jwt.exceptions.PyJWTError:
            return False
        except ExpiredTokenException:
            return False
        except DecodeTokenException:
            return False
        if not user_id:
            return False
        if user_id != user_id_from_token:
            return False
        return True

    async def connect(self, key: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[key] = websocket

    def disconnect(self, key: str):
        del self.active_connections[key]


conn_manager = ConnectionManager()
