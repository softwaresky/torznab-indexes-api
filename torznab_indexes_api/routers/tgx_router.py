import pprint
from typing import Annotated

from fastapi import APIRouter, Query, Depends, Response

from torznab_indexes_api.schemas import FunctionType, AllParamsSchemas, TGxRequestSchema

from torznab_indexes_api.core.exceptions import RequestErrorException, ServerErrorException
from torznab_indexes_api.services.tgx_service import TGxService

router = APIRouter()


@router.get("/api")
async def search(
        function_type: Annotated[FunctionType, Query(alias="t")] = FunctionType.search,
        apikey: str = "",
        search_params: AllParamsSchemas = Depends(),
):
    tgx_service = TGxService()
    if FunctionType.caps == function_type:
        data = await tgx_service.get_capabilities()
    elif function_type in [FunctionType.search, FunctionType.movie, FunctionType.tvsearch]:
        reqeust_schema = TGxRequestSchema.model_validate(
            {
                "search_params": search_params.model_dump(exclude_none=True, exclude_unset=True, by_alias=True),
            }
        )
        data = await tgx_service.search(reqeust_schema=reqeust_schema)
    else:
        raise RequestErrorException(
            context={"message": f"Unsupported function `{function_type.value}`."},
        )
    return Response(content=data, media_type="application/rss+xml")
