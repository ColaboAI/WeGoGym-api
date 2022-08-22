"""
You can have several authentication methods, e.g. a cookie
authentication for browser-based queries and a JWT token authentication for pure API queries.

In this template, token will be sent through Bearer header
{"Authorization": "Bearer xyz"}
using JWT tokens.

There are more option to consider, refer to
https://fastapi-users.github.io/fastapi-users/configuration/authentication/

UserManager class is core fastapi users class with customizable attrs and methods
https://fastapi-users.github.io/fastapi-users/configuration/user-manager/
"""


import os
from typing import Optional
import uuid

from fastapi import Request, Depends
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.manager import BaseUserManager, UUIDIDMixin
from fastapi_users import FastAPIUsers
from httpx_oauth.clients.google import GoogleOAuth2

from app.schemas.user import UserRead
from app.core import config
from app.session import get_user_db

google_oauth_client = GoogleOAuth2(
    os.getenv("GOOGLE_OAUTH_CLIENT_ID", ""),
    os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", ""),
)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=config.settings.SECRET_KEY,
        lifetime_seconds=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


BEARER_TRANSPORT = BearerTransport(tokenUrl="auth/jwt/login")
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=BEARER_TRANSPORT,
    get_strategy=get_jwt_strategy,
)


class UserManager(UUIDIDMixin, BaseUserManager[UserRead, uuid.UUID]):
    reset_password_token_secret = config.settings.SECRET_KEY
    verification_token_secret = config.settings.SECRET_KEY

    async def on_after_register(
        self, user: UserRead, request: Optional[Request] = None
    ):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: UserRead, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: UserRead, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[UserRead, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
