from app.core.exceptions.base import CustomException


class PostNotFound(CustomException):
    """Raised when a post is not found."""

    code = 404
    error_code = "POST__NOT_FOUND"
    message = "post not found"


class CommentNotFound(CustomException):
    """Raised when a comment is not found."""

    code = 404
    error_code = "COMMENT__NOT_FOUND"
    message = "comment not found"


class CommunityNotFound(CustomException):
    """Raised when a community is not found."""

    code = 404
    error_code = "COMMUNITY__NOT_FOUND"
    message = "community not found"


class Forbidden(CustomException):
    """Raised when a user is not authorized to do something."""

    code = 403
    error_code = "FORBIDDEN"
    message = "forbidden"
