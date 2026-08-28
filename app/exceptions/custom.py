from app.exceptions.base import AppException


class InvalidTokenError(AppException):
    status_code = 401
    detail = "Invalid token."