from torznab_indexes_api.schemas.rarbg_schemas import FunctionType
from torznab_indexes_api.services.rarbg_service import RarbgService

from torznab_indexes_api.routers.base_router import BaseRouter


class RarbgRouter(BaseRouter):
    function_type = FunctionType
    service = RarbgService()

router = RarbgRouter().router