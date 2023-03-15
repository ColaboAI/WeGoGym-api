from fastapi import WebSocketException, status


class WSTokenExpired(WebSocketException):
    def __init__(
        self,
        code: int = status.WS_1008_POLICY_VIOLATION,
        reason: str = "Access Token is expired",
    ) -> None:
        super().__init__(code, reason)


class WSInvalidToken(WebSocketException):
    def __init__(
        self, code: int = status.WS_1008_POLICY_VIOLATION, reason: str = "Invalid token"
    ) -> None:
        super().__init__(code, reason)


class WSUserNotInChatRoom(WebSocketException):
    def __init__(
        self,
        code: int = status.WS_1008_POLICY_VIOLATION,
        reason: str = "User not in chat room",
    ) -> None:
        super().__init__(code, reason)


class WSInternalError(WebSocketException):
    def __init__(
        self,
        code: int = status.WS_1008_POLICY_VIOLATION,
        reason: str = "Internal error",
    ) -> None:
        super().__init__(code, reason)
