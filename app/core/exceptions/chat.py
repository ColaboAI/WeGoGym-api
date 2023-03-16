from app.core.exceptions.base import CustomException


class UserNotInChatRoom(CustomException):
    code = 404
    error_code = "USER__NOT_IN_CHAT_ROOM"
    message = "user not in chat room"


class ChatRoomNotFound(CustomException):
    code = 404
    error_code = "CHAT_ROOM__NOT_FOUND"
    message = "chat room not found"


class ChatMemberNotFound(CustomException):
    code = 404
    error_code = "CHAT_MEMBER__NOT_FOUND"
    message = "chat member not found"


class NoDirectChatRoom(CustomException):
    code = 404
    error_code = "NO_DIRECT_CHAT_ROOM"
    message = "no direct chat room"
