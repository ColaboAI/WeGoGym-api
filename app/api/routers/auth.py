from fastapi import APIRouter, Response

from app.schemas.auth import (
    RefreshTokenRequest,
    VerifyTokenRequest,
    RefreshTokenResponse,
)
from app.services.jwt_service import JwtService
from app.schemas import ExceptionResponseSchema

auth_router = APIRouter()


@auth_router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def refresh_token(request: RefreshTokenRequest):
    token = await JwtService().create_refresh_token(
        token=request.token, refresh_token=request.refresh_token
    )
    return {"token": token.token, "refresh_token": token.refresh_token}


@auth_router.post("/verify")
async def verify_token(request: VerifyTokenRequest):
    await JwtService().verify_token(token=request.token)
    return Response(status_code=200)
