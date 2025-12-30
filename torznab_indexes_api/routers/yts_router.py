from fastapi import APIRouter, Depends, Response, Query
from torznab_indexes_api.schemas.yts_schemas import YTSRequestSchema, AllParamsSchemas, FunctionType
from torznab_indexes_api.core.exceptions import RequestErrorException
from torznab_indexes_api.services.yts_service import YTSService

from torznab_indexes_api.routers.base_router import BaseRouter


class YTSRouter(BaseRouter):
    request_schema = YTSRequestSchema()
    params = AllParamsSchemas
    function_type = FunctionType
    service = YTSService()

router = YTSRouter().router

# router = APIRouter()
#
# @router.get("/api")
# async def search(
#         apikey: str = "",
#         function_type: FunctionType = Query(default=FunctionType.search, alias="t"),
#         search_params: AllParamsSchemas = Depends(),
# ):
#     yts_service = YTSService()
#     if function_type == FunctionType.caps:
#         data = await yts_service.get_capabilities()
#     elif function_type in list(FunctionType):
#         request_schema = YTSRequestSchema.model_validate({
#             "search_params": search_params.model_dump(exclude_none=True, exclude_unset=True, by_alias=True),
#         })
#         data = await yts_service.search(request_schema=request_schema)
#     else:
#         raise RequestErrorException(
#             context={"message": f"Unsupported function `{function_type}`."},
#         )
#     return Response(content=data, media_type="application/rss+xml")
