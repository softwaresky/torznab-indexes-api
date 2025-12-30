from enum import Enum

from typing import Generic, TypeVar, Type

from fastapi import APIRouter, Query, Depends, Response

from pydantic import BaseModel
from torznab_indexes_api.services.base_service import BaseService
from torznab_indexes_api.schemas.torznab_schemas import FunctionType
from torznab_indexes_api.core.exceptions import RequestErrorException


TParams = TypeVar("TParams", bound=BaseModel)


class BaseRouter(Generic[TParams]):
    request_schema: Type[BaseModel]
    function_type: FunctionType
    params: TParams
    service: BaseService

    def __init__(self):
        self.router = APIRouter()

        function_types = self.get_function_types()
        index = list(function_types).index(FunctionType.search) if FunctionType.search in function_types else 0

        @self.router.get("/api")
        async def search(
                apikey: str = "",
                function_type: function_types = Query(default=list(function_types)[index], alias="t"),
                search_params: TParams = Depends(self.get_params()),
        ):
            if function_type == function_types.caps:
                data = await self.service.get_capabilities()
            elif function_type in list(function_types):
                request_schema = self.request_schema.model_validate({
                    "search_params": search_params.model_dump(exclude_none=True, exclude_unset=True, by_alias=True),
                })
                data = await self.service.search(request_schema=request_schema)
            else:
                raise RequestErrorException(
                    context={"message": f"Unsupported function `{function_type}`."},
                )
            return Response(content=data, media_type="application/rss+xml")

    def get_params(self) -> TParams:
        return self.params

    def get_function_types(self) -> FunctionType:
        return self.function_type