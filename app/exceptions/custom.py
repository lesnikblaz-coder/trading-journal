from app.exceptions.base import AppException



class InvalidTokenError(AppException):
    status_code = 401
    detail = "Invalid token."

class InvalidCredentialsError(AppException):
    status_code = 401
    detail = "Invalid authentication credentials."

class UserNotFoundError(AppException):
    status_code = 404
    detail = "User not found."

class DuplicateEmailError(AppException):
    status_code = 409
    detail = "Email already in use."

class InsufficientPermissions(AppException):
    status_code = 403
    detail = "Insufficient permissions."

class EntityNotFoundError(AppException):
    status_code = 404
    detail = "Entity not found."

class InvalidTradingSystemError(AppException):
    status_code = 401
    detail = "Non-existent trading system."

class InvalidTradeDataValuesError(AppException):
    status_code = 422
    detail = "Invalid trade data (entry/stop loss/exit price for trade direction)."