from fastapi import Depends, FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware

from app.api.api import api_router
from app.core.config import settings
from app.core.helpers.cache import Cache, RedisBackend, CustomKeyMaker
from app.api.websockets.chat import chat_ws_router
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware


def init_cache() -> None:
    Cache.init(backend=RedisBackend(), key_maker=CustomKeyMaker())


def get_application():

    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
    ]
    _app = FastAPI(title=settings.PROJECT_NAME, middleware=middleware)
    init_cache()
    return _app


app = get_application()

app.include_router(api_router)
app.include_router(chat_ws_router, tags="websocket_chat")
