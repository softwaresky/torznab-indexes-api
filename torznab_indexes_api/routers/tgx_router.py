from typing import Annotated

from fastapi import APIRouter, Query, Depends, Response

from torznab_indexes_api.schemas import FunctionType, AllParamsSchemas

from torznab_indexes_api.core.exceptions import RequestErrorException
from torznab_indexes_api.services.tgx_service import TGxService

router = APIRouter()


@router.get("/api")
async def search(
        function_type: Annotated[FunctionType, Query(alias="t")] = FunctionType.search,
        apikey: str = "",
        search: AllParamsSchemas = Depends(),
):

    tgx_service = TGxService()
    if FunctionType.caps == function_type:
        data = await tgx_service.get_capabilities()
    elif function_type in [FunctionType.search, FunctionType.movie, FunctionType.tvsearch]:
        data = await tgx_service.search(function_type=function_type, search_params=search)
    else:
        raise RequestErrorException(
            context={"message": f"Unsupported function `{function_type.value}`."},
        )
    return Response(content=data, media_type="application/rss+xml")
