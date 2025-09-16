import logging

from pydantic import ValidationError

from torznab_indexes_api.core.exceptions import ServerErrorException
from torznab_indexes_api.core.clients.tgx_client import TGxClient
from torznab_indexes_api.schemas import (
    FunctionType, SearchSchema, MovieSearchSchema, TvSearchSchema, AllParamsSchemas,
    TgxItemSchema, RssResult, NewznabGuid, NewznabItem, NewznabChannel, NewznabEnclosure, NewznabTorznabAttr,
    RssCapabilitiesSchema, BaseXmlModel, CategoryEnum
)

logger = logging.getLogger(__name__)


class TGxService:

    def __init__(self):
        self._map_functions = {
            FunctionType.search: SearchSchema,
            FunctionType.tvsearch: TvSearchSchema,
            FunctionType.movie: MovieSearchSchema,
        }

    @staticmethod
    def _response(schema: BaseXmlModel) -> str:
        return schema.to_xml(
            pretty_print=True,
            encoding="UTF-8",
            standalone=True
        )

    async def search(
            self,
            function_type: FunctionType,
            search_params: AllParamsSchemas
    ) -> str:

        logger.info("Search `%s` function with search params: `%s`",
                    function_type.value,
                    search_params.model_dump_json(exclude_none=True, exclude_unset=True))

        schema_class = self._map_functions[function_type]
        try:
            search_schema = schema_class.model_validate(search_params.model_dump(
                exclude_unset=True, exclude_none=True
            ))
        except ValueError as err:
            raise ServerErrorException(
                context={
                    "message": f"`{function_type.value}` functions has unsupported parameters",
                    "error": str(err)
                }
            )

        items = []
        async with TGxClient() as tgx_client:
            async for item_ in tgx_client.fetch_data(
                    search_terms=search_schema.search_terms(),
                    category_enum=search_schema.category,
                    page=search_schema.page,
                    recursive=False
            ):
                try:
                    tgx_item = TgxItemSchema.model_validate(item_)
                    tv_attrs = []
                    if season := tgx_item.title_parsed_data.get("season"):
                        tv_attrs.append(
                            NewznabTorznabAttr(name="season", value=str(season))
                        )
                    if episode := tgx_item.title_parsed_data.get("episode"):
                        tv_attrs.append(
                            NewznabTorznabAttr(name="episode", value=str(episode))
                        )
                    items.append(NewznabItem(
                        title=tgx_item.name,
                        guid=NewznabGuid(
                            title=tgx_item.torrent_url
                        ),
                        link=tgx_item.download_url,
                        comments=tgx_item.torrent_url,
                        pubDate=tgx_item.added.strftime("%a, %d %b %Y %H:%M:%S %z"),
                        description=f"Uploader: {tgx_item.uploader}",
                        category=tgx_item.category,
                        enclosure=NewznabEnclosure(
                            url=tgx_item.download_url,
                            type="application/x-bittorrent"
                        ),
                        attrs=[
                            NewznabTorznabAttr(name="size", value=str(tgx_item.size)),
                            NewznabTorznabAttr(name="infohash", value=tgx_item.hash),
                            NewznabTorznabAttr(name="guid", value=tgx_item.hash),
                            NewznabTorznabAttr(name="seeders", value=str(tgx_item.seeders)),
                            NewznabTorznabAttr(name="peers", value=str(tgx_item.leechers)),
                            NewznabTorznabAttr(name="leechers", value=str(tgx_item.leechers)),
                            NewznabTorznabAttr(name="category", value="5000"), # Hardcoded for now
                            NewznabTorznabAttr(name="language", value=tgx_item.language),
                            NewznabTorznabAttr(name="downloadvolumefactor", value="0"),
                            NewznabTorznabAttr(name="uploadvolumefactor", value="1"),
                            NewznabTorznabAttr(name="uploader", value=tgx_item.uploader),
                            NewznabTorznabAttr(name="tags", value=",".join(tgx_item.tags)),
                        ] + tv_attrs
                    ))
                except ValidationError as err:
                    logger.error("Failed validation on `%s`. Data: `%s`",
                                 TgxItemSchema.__class__.__name__,
                                 err.json(include_url=False)
                                 )

        logger.info("Found `%d` torrents", len(items))
        result = RssResult(
            channel=NewznabChannel(
                title="TGx",
                description="Torrent Galaxy site",
                link=TGxClient.base_url,
                item=items
            )
        )
        return self._response(result)

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
