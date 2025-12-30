import logging
from typing import Type
from pydantic import BaseModel
from torznab_indexes_api.schemas.torznab_schemas import BaseXmlModel, RssCapabilitiesSchema, CategoryEnum, FunctionType

logger = logging.getLogger(__name__)

class BaseService:

    @staticmethod
    def _response(schema: BaseXmlModel) -> str:
        return schema.to_xml(
            pretty_print=True,
            encoding="UTF-8",
            standalone=True
        )

    async def search(self, request_schema: BaseModel) -> str:
        raise NotImplementedError()


    async def get_capabilities(self):

        # categories_map = defaultdict(list)
        # categories = []
        # for index_, (cat, sub_cats) in enumerate(categories_map.items(), start=100):
        #     categories.append({
        #         "name": cat,
        #         "id": f"{index_}" if cat.lower() != "tv" else "5000",
        #         "sub_cats": sub_cats
        #     })

        categories = []
        for index_, cat, in zip([5000, 2000], CategoryEnum.__members__):
            categories.append({
                "name": cat,
                "id": f"{index_}",
            })

        result = RssCapabilitiesSchema(
            **{
                "server": {
                    "title": "torznab-indexes-api"
                },
                "limits": {
                    "default": "50",
                    "max": "50"
                },
                "searching": {
                    "search": {
                        "available": "yes",
                        "supportedParams": "q"
                    },
                    "tv_search": {
                        "available": "yes",
                        "supportedParams": "q,imdbid,season,ep"
                    },
                    "movie_search": {
                        "available": "yes",
                        "supportedParams": "q,imdbid"
                    },
                    "audio_search": {
                        "available": "yes",
                        "supportedParams": "q"
                    },
                    "book_search": {
                        "available": "yes",
                        "supportedParams": "q"
                    }
                },
                "categories": {
                    "categories": categories,
                },
            }
        )

        return self._response(result)