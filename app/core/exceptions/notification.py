from . import CustomException


class NotificaitonNotFoundException(CustomException):
    code = 404
    error_code = "NOTIFICATION__NOT_FOUND"
    message = "notificaton not found"


class NotAdminOfNotificationException(CustomException):
    code = 400
    error_code = "NOTIFICATION__NOT_ADMIN"
    message = "not admin of notification"
