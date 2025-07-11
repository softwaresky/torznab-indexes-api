import logging
import inspect

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

logger = logging.getLogger(__name__)

class AppExceptionCase(Exception):
    def __init__(self, status_code: int, context: dict | None):
        super().__init__()

        self.exception_case = self.__class__.__name__
        self.status_code = status_code
        self.context = context

    def __str__(self):
        return (
            f"<AppException {self.exception_case} - "
            + f"status_code={self.status_code} - context={self.context}>"
        )


class ServerErrorException(AppExceptionCase):
    def __init__(self, context: dict | None):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        super().__init__(status_code=status_code, context=context)


class RequestErrorException(AppExceptionCase):
    def __init__(self, context: dict | None):
        status_code = status.HTTP_400_BAD_REQUEST
        super().__init__(status_code=status_code, context=context)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


def caller_info() -> str:
    info = inspect.getframeinfo(inspect.stack()[2][0])
    return f"{info.filename}:{info.function}:{info.lineno}"


async def app_exception_handler(request: Request, exc: AppExceptionCase):
    logger.error("%s | caller=%s", exc, caller_info())
    return JSONResponse(
        status_code=exc.status_code,
        content={"app_exception": exc.exception_case, "context": exc.context},
    )