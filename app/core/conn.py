from uuid import UUID
from fastapi import WebSocket
import jwt
from app.core.exceptions.token import DecodeTokenException, ExpiredTokenException
from app.core.exceptions.websocket import WSInvalidToken, WSTokenExpired

from app.utils.token_helper import TokenHelper
from starlette.websockets import WebSocketState

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
            raise WSInvalidToken
        except ExpiredTokenException:
            raise WSTokenExpired
        except DecodeTokenException:
            raise WSInvalidToken
        if not user_id:
            return False
        if user_id != user_id_from_token:
            return False
        return True

    async def connect(self, key: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[key] = websocket

    async def disconnect(self, key: str):
        if key in self.active_connections:
            if self.active_connections[key].client_state == WebSocketState.CONNECTED:
                await self.active_connections[key].close()
            del self.active_connections[key]

    async def close_all(self):
        for key in self.active_connections:
            if self.active_connections[key].client_state == WebSocketState.CONNECTED:
                await self.active_connections[key].close()
        self.active_connections = {}


conn_manager = ConnectionManager()
