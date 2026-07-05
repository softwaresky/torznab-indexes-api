from typing import Generic, TypeVar

from fastapi import APIRouter, Query, Response, Depends

from pydantic import BaseModel
from torznab_indexes_api.services.base_service import BaseService
from torznab_indexes_api.schemas.torznab_schemas import (
    FunctionType, AllParamsSchemas, SearchParams, TvSearchParams, MovieSearchParams, AudioSearchParams, BookSearchParams
)
from torznab_indexes_api.core.exceptions import RequestErrorException


TParams = TypeVar("TParams", bound=BaseModel)


class BaseRouter(Generic[TParams]):
    function_type: FunctionType
    service: BaseService

    def __init__(self):
        self.router = APIRouter()

        function_types = self.get_function_types()
        index = list(function_types).index(FunctionType.search) if FunctionType.search in function_types else 0

        @self.router.get("/api")
        async def search(
                function_type: function_types = Query(default=list(function_types)[index], alias="t"),
                search_params: AllParamsSchemas = Depends(),
        ):

            data: str = ""
            search_data = search_params.model_dump(mode="json", by_alias=True)
            match function_type:
                case FunctionType.caps:
                    data = await self.service.get_capabilities()
                case FunctionType.search:
                    data = await  self.service.search(request_params=SearchParams.model_validate(search_data))
                case FunctionType.tvsearch:
                    data = await self.service.tv_search(request_params=TvSearchParams.model_validate(search_data))
                case FunctionType.movie:
                    data = await self.service.movie_search(request_params=MovieSearchParams.model_validate(search_data))
                case _:
                    raise RequestErrorException(
                        context={"message": f"Unsupported function `{function_type}`."},
                    )
            return self.xml_response(content=data)

    @staticmethod
    def xml_response(content: str) -> Response:
        return Response(content=content, media_type="application/xml")


    def get_function_types(self) -> FunctionType:
        return self.function_type