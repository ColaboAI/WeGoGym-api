from app.core.exceptions.base import CustomException


class UserNotInChatRoom(CustomException):
    code = 404
    error_code = "USER__NOT_IN_CHAT_ROOM"
    message = "user not in chat room"
