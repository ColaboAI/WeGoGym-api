import asyncio
import signal
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from fastapi.responses import JSONResponse, PlainTextResponse

from app.api.api import api_router
from app.core import conn
from app.core.config import settings
from app.core.exceptions.base import CustomException
from app.core.helpers.cache import Cache, RedisBackend, CustomKeyMaker
from app.api.websockets.chat import chat_ws_router
from app.core.fastapi.middlewares import (
    AuthBackend,
    AuthenticationMiddleware,
)


def init_router(app_: FastAPI) -> None:
    app_.include_router(api_router)
    app_.include_router(chat_ws_router)


def init_cache() -> None:
    Cache.init(backend=RedisBackend(), key_maker=CustomKeyMaker())


HANDLED_SIGNALS = (signal.SIGINT, signal.SIGTERM)


def init_listeners(app_: FastAPI) -> None:
    # Exception handler
    @app_.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.code,
            content={"error_code": exc.error_code, "message": exc.message},
        )

    # TODO: Remove this(only for debug)
    @app_.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
        print(f"{request}: {exc_str}")
        content = {"status_code": 10422, "message": exc_str, "detail": exc.errors()}

        return JSONResponse(content=jsonable_encoder(content), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @app_.exception_handler(ResponseValidationError)
    async def response_val_error(request, exc):
        exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
        print(f"{request}: {exc_str}")
        content = {"status_code": 10422, "message": exc_str, "detail": exc.errors()}

        return JSONResponse(content=jsonable_encoder(content), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    # Graceful shutdown
    @app_.on_event("shutdown")
    async def shutdown_event():
        print("Shutting down...")
        await conn.conn_manager.close_all()
        print("All connections closed.")
        print("Stop event loop...")
        loop = asyncio.get_running_loop()
        loop.stop()
        print("Event loop stopped.")


def on_auth_error(request: Request, exc: Exception):
    status_code, error_code, message = 401, None, str(exc)
    if isinstance(exc, CustomException):
        status_code = int(exc.code)
        error_code = exc.error_code
        message = exc.message

    return JSONResponse(
        status_code=status_code,
        content={"error_code": error_code, "message": message},
    )


def make_middleware() -> list[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(
            AuthenticationMiddleware,
            backend=AuthBackend(),
            on_error=on_auth_error,
        ),
    ]
    return middleware


def get_application() -> FastAPI:
    _app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        docs_url=None if settings.ENVIRONMENT == "PRODUCTION" else "/docs",
        redoc_url=None if settings.ENVIRONMENT == "PRODUCTION" else "/redoc",
        middleware=make_middleware(),
    )
    init_router(app_=_app)
    init_listeners(app_=_app)
    init_cache()
    return _app


app = get_application()
