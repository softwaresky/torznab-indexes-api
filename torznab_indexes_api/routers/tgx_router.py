from torznab_indexes_api.schemas.tgx_schemas import FunctionType
from torznab_indexes_api.services.tgx_service import TGxService

from torznab_indexes_api.routers.base_router import BaseRouter


class TGxRouter(BaseRouter):
    function_type = FunctionType
    service = TGxService()

router = TGxRouter().router
