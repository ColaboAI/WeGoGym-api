from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware

from app.api.api import api_router
from app.core.config import settings


def get_application():

    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]
    print(settings.BACKEND_CORS_ORIGINS)
    print([str(origin) for origin in settings.BACKEND_CORS_ORIGINS])
    _app = FastAPI(title=settings.PROJECT_NAME, middleware=middleware)

    return _app


app = get_application()
app.include_router(api_router)
