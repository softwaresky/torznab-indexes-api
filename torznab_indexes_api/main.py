import logging.config

import uvicorn

from fastapi import FastAPI
from fastapi.exceptions import HTTPException

from torznab_indexes_api.core.exceptions import (
    AppExceptionCase, app_exception_handler, http_exception_handler
)

from torznab_indexes_api.routers import tgx_router
from torznab_indexes_api.core.config.logging import get_logging_config

logging.config.dictConfig(get_logging_config())


def create_app() -> FastAPI:
    app = FastAPI(
        title="Torznab Indexes API",
        openapi_url="/openapi.json",
    )

    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request, e):
        return await http_exception_handler(request, e)

    @app.exception_handler(AppExceptionCase)
    async def custom_app_exception_handler(request, e):
        return await app_exception_handler(request, e)

    app.include_router(tgx_router, prefix="/tgx")

    return app


if __name__ == '__main__':
    uvicorn.run(create_app(), host="0.0.0.0", port=8000)
