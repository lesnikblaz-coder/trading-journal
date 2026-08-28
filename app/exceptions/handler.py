from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.base import AppException
from app.core.logging_config import logger

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):

        logger.exception(
            "Exception on %s %s: %s",
            request.method,
            request.url.path,
            exc
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": str(exc)
            }
        )