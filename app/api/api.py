from fastapi.responses import HTMLResponse

from fastapi import APIRouter, Depends, WebSocket

from app.api.routers.audio import audio_router
from app.api.routers.chat import chat_router
from app.api.routers.auth import auth_router
from app.api.routers.user import user_router

api_router = APIRouter()


@api_router.get("/")
async def get():
    return HTMLResponse(html)


api_router.include_router(
    audio_router,
    prefix="/audio",
    tags=["audio"],
)

api_router.include_router(
    chat_router,
    prefix="/chat",
    tags=["chat"],
)

api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"],
)

api_router.include_router(
    user_router,
    prefix="/user",
    tags=["user"],
)

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>Chat</h1>
        <h2>Room: <span id="room-id"></span><br> Your ID: <span id="client-id"></span></h2>
        <label>Room: <input type="text" id="channelId" autocomplete="off" value="foo"/></label>
        <button onclick="connect(event)">Connect</button>
        <hr>
        <form style="position: absolute; bottom:0" action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = null;
            function connect(event) {
                var client_id = Date.now()
                document.querySelector("#client-id").textContent = client_id;
                document.querySelector("#room-id").textContent = channelId.value;
                if (ws) ws.close()
                ws = new WebSocket(`ws://localhost:8000/ws/chat/${channelId.value}/${client_id}`);
                
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
                event.preventDefault();
                
            }
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
                document.getElementById("messageText").focus()
            }
            
        </script>
    </body>
</html>
"""
