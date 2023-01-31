from app.core.exceptions import CustomException


class PasswordDoesNotMatchException(CustomException):
    code = 401
    error_code = "USER__PASSWORD_DOES_NOT_MATCH"
    message = "password does not match"


class DuplicatePhoneNumberOrUsernameException(CustomException):
    code = 400
    error_code = "USER__DUPLICATE_PHONE_NUMBER_OR_USERNAME"
    message = "duplicate phone number or username"


class UserNotFoundException(CustomException):
    code = 404
    error_code = "USER__NOT_FOUND"
    message = "user not found"
