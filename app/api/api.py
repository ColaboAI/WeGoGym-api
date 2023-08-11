from fastapi.responses import HTMLResponse

from fastapi import APIRouter

from app.api.routers.audio import audio_router
from app.api.routers.chat import chat_router
from app.api.routers.auth import auth_router
from app.api.routers.user import user_router
from app.api.routers.workout_promise import workout_promise_router
from app.api.routers.notification import notification_router
from app.api.routers.voc import voc_router
from app.api.routers.version import version_router
from app.api.routers.community import router as community_router

api_router = APIRouter(prefix="/api/v1")


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

api_router.include_router(
    workout_promise_router,
    prefix="/workout-promise",
    tags=["workout-promise"],
)

api_router.include_router(
    notification_router,
    prefix="/notification",
    tags=["notification"],
)

api_router.include_router(
    voc_router,
    prefix="/voc",
    tags=["voc"],
)

api_router.include_router(
    version_router,
    prefix="/version",
    tags=["version"],
)

api_router.include_router(
    community_router,
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
        <label>User id: <input type="text" id="clientID" autocomplete="off" value="bar"/></label>
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
                document.querySelector("#client-id").textContent = clientID.value;
                document.querySelector("#room-id").textContent = channelId.value;
                if (ws) ws.close()
                ws = new WebSocket(`ws://localhost:8000/api/v1/ws/chat/${channelId.value}/${clientID.value}`);
                
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
                ws.send(JSON.stringify({
                text: input.value,
                })) 
                input.value = ''
                event.preventDefault()
                document.getElementById("messageText").focus()
            }
            
        </script>
    </body>
</html>
"""
