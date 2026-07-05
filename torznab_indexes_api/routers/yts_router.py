from torznab_indexes_api.schemas.yts_schemas import FunctionType
from torznab_indexes_api.services.yts_service import YTSService
from torznab_indexes_api.routers.base_router import BaseRouter


class YTSRouter(BaseRouter):
    function_type = FunctionType
    service = YTSService()

router = YTSRouter().router

