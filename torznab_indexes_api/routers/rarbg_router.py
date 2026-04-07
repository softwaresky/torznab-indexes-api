from fastapi import APIRouter, Depends, Response, Query
from torznab_indexes_api.schemas.rarbg_schemas import RarbgRequestSchema, AllParamsSchemas, FunctionType
from torznab_indexes_api.core.exceptions import RequestErrorException
from torznab_indexes_api.services.rarbg_service import RarbgService

from torznab_indexes_api.routers.base_router import BaseRouter


class RarbgRouter(BaseRouter):
    request_schema = RarbgRequestSchema()
    params = AllParamsSchemas
    function_type = FunctionType
    service = RarbgService()

router = RarbgRouter().router