from app.schemas.jwt import RefreshTokenSchema
from app.core.exceptions.token import DecodeTokenException, ExpiredTokenException
from app.utils.token_helper import TokenHelper


class JwtService:
    async def verify_token(self, token: str) -> None:
        TokenHelper.decode(token=token)

    async def create_refresh_token(
        self,
        token: str,
        refresh_token: str,
    ) -> RefreshTokenSchema:
        dec_token = None
        try:
            dec_token = TokenHelper.decode(token=token)
        except ExpiredTokenException:
            dec_token = TokenHelper.decode_expired_token(token=token)

        dec_refresh_token = TokenHelper.decode(token=refresh_token)

        if dec_refresh_token.get("sub") != "refresh":
            raise DecodeTokenException("Invalid refresh token")

        return RefreshTokenSchema(
            token=TokenHelper.encode(payload={"user_id": dec_token.get("user_id")}),
            refresh_token=TokenHelper.encode(
                payload={"sub": "refresh"}, expire_period=60 * 60 * 24 * 30
            ),
        )
