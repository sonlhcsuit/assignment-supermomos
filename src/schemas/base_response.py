from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, ValidationError

from src.schemas.exceptions.base import AppException

T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    message: str | None
    data: T | None

    def __init__(
        self,
        data: T | None = None,
        message: str | None = None,
    ):
        super().__init__(data=data, message=message)

    @classmethod
    def success(cls, data: T) -> 'BaseResponse[T]':
        return cls(data=data)

    @classmethod
    def error(cls, error: Exception) -> 'BaseResponse':
        data = None
        if isinstance(error, AppException):
            message = error.message

            if hasattr(error, 'details'):
                data = error.details

        elif isinstance(error, ValueError):
            message = error.args[0] if len(error.args) > 0 else str(error)
        elif isinstance(error, ValidationError):
            message = error.title
        else:
            message = str(error)

        return cls(data=data, message=message)

    @classmethod
    def accepted(cls, data: T, message: str = 'Accepted') -> 'BaseResponse':
        return cls(data=data, message=message)
