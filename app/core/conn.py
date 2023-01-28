from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.actice_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.actice_connections[websocket] = websocket

    def disconnect(self, websocket: WebSocket):
        del self.actice_connections[websocket]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.actice_connections.values():
            await connection.send_json(message, mode="text")


conn_manager = ConnectionManager()
