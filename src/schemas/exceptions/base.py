from enum import IntEnum


class ErrorCode(IntEnum):
    AUTH = 401
    BAD_GATEWAY = 400
    FORBIDDEN = 403
    INTERNAL_SERVER_ERROR = 500
    BAD_REQUEST = 400
    NOT_FOUND = 404
    EXTERNAL_SERVICE_ERROR = 503


class InternalErrorCode(IntEnum):
    UNKNOWN_ERROR = 1000
    MISSING_SHEET = 1001
    MISSING_COLUMN = 1002
    INVALID_DATA = 1003
    EMPTY_FILE = 1004


class AppException(Exception):
    error_code = ErrorCode.INTERNAL_SERVER_ERROR
    message = 'Internal Server Error'

    def __init__(self, message: str, error_code: ErrorCode):
        if message:
            self.message = message

        self.error_code = error_code


class AuthException(AppException):
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.AUTH):
        super().__init__(message, error_code)


class ForbiddenException(AppException):
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.FORBIDDEN):
        super().__init__(message, error_code)


class BadRequestException(AppException):
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.BAD_REQUEST):
        super().__init__(message, error_code)


class BadRequestExceptionWithDetails(AppException):
    def __init__(
        self,
        message: str,
        details: dict,
        error_code: ErrorCode = ErrorCode.BAD_REQUEST,
        internal_error_code: InternalErrorCode = InternalErrorCode.UNKNOWN_ERROR,
    ):
        self.message = message
        self.error_code = error_code
        self.details = {
            'error_code': internal_error_code.value,
            'error_message': message,
            'details': details,
        }


class NotFoundException(AppException):
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.NOT_FOUND):
        super().__init__(message, error_code)


class InternalServerException(AppException):
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR):
        super().__init__(message, error_code)
