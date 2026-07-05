import logging
from torznab_indexes_api.schemas.torznab_schemas import (
    BaseXmlModel, RssCapabilitiesSchema, CategoryEnum, SearchParams, TvSearchParams, MovieSearchParams,
    AudioSearchParams, BookSearchParams
)

logger = logging.getLogger(__name__)

class BaseService:

    @staticmethod
    def _response(schema: BaseXmlModel) -> str:
        return schema.to_xml(
            pretty_print=True,
            encoding="UTF-8",
            standalone=True
        )

    async def search(self, request_params: SearchParams) -> str:
        raise NotImplementedError()

    async def tv_search(self, request_params: TvSearchParams) -> str:
        raise NotImplementedError()

    async def movie_search(self, request_params: MovieSearchParams) -> str:
        raise NotImplementedError()

    async def audio_search(self, request_params: AudioSearchParams) -> str:
        raise NotImplementedError()

    async def book_search(self, request_params: BookSearchParams) -> str:
        raise NotImplementedError()

    @classmethod
    def get_categories(cls):
        return [
            {
                "name": cat,
                "id": f"{index_}",
            }
            for index_, cat, in zip([5000, 2000], CategoryEnum.__members__)
        ]


    async def get_capabilities(self):

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
                    "categories": self.get_categories(),
                },
            }
        )

        return self._response(result)