from . import CustomException


class WorkoutPromiseNotFoundException(CustomException):
    code = 404
    error_code = "WORKOUT_PROMISE__NOT_FOUND"
    message = "workout promise not found"


class WorkoutPromiseAlreadyExistException(CustomException):
    code = 400
    error_code = "WORKOUT_PROMISE__ALREADY_EXIST"
    message = "workout promise already exist"


class GymInfoNotFoundException(CustomException):
    code = 404
    error_code = "GYM_Info__NOT_FOUND"
    message = "gym info not found"


class WorkoutParticipantNotFoundException(CustomException):
    code = 404
    error_code = "WORKOUT_PARTICIPANT__NOT_FOUND"
    message = "workout participant not found"


class AlreadyJoinedWorkoutPromiseException(CustomException):
    code = 400
    error_code = "WORKOUT_PARTICIPANT__ALREADY_JOINED"
    message = "already joined workout promise"


class WorkoutPromiseIsFullException(CustomException):
    code = 400
    error_code = "WORKOUT_PROMISE__IS_FULL"
    message = "workout promise is full"


class WorkoutPromiseIsWrongException(CustomException):
    code = 500
    error_code = "WORKOUT_PROMISE__IS_WRONG_IN_DB"
    message = "workout promise is wrong... please check db"


class NotAdminOfWorkoutPromiseException(CustomException):
    code = 400
    error_code = "WORKOUT_PROMISE__NOT_ADMIN"
    message = "not admin of workout promise"