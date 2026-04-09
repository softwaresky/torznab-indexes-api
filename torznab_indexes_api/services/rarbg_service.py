import logging
from urllib.parse import urljoin
from torznab_indexes_api.core.clients.rarbg_client import RarbgClient
from torznab_indexes_api.schemas.rarbg_schemas import RarbgRequestSchema
from torznab_indexes_api.services.base_service import BaseService
from torznab_indexes_api.schemas.torznab_schemas import (
    RssResult, NewznabGuid, NewznabItem, NewznabChannel, NewznabEnclosure, NewznabTorznabAttr, RssCapabilitiesSchema, CategoryEnum
)

logger = logging.getLogger(__name__)


class RarbgService(BaseService):

    async def search(self, request_schema: RarbgRequestSchema) -> str:

        logger.info("Search with search params: `%s`", request_schema)

        items = []
        async with RarbgClient() as client:
            async for rarbg_item in client.fetch_data(request_schema=request_schema):
                torrent_url = urljoin(client.base_url, rarbg_item.file_link)
                items.append(NewznabItem(
                    title=f"{rarbg_item.release_name or rarbg_item.file}",
                    guid=NewznabGuid(
                        title=torrent_url
                    ),
                    link=rarbg_item.magnet_link,
                    comments=torrent_url,
                    pubDate=rarbg_item.added.strftime("%a, %d %b %Y %H:%M:%S %z"),
                    description="",
                    category=rarbg_item.categories[0],
                    enclosure=NewznabEnclosure(
                        url=rarbg_item.magnet_link,
                        type="application/x-bittorrent"
                    ),
                    attrs=[
                        NewznabTorznabAttr(name="size", value=str(rarbg_item.size_bytes)),
                        # NewznabTorznabAttr(name="infohash", value=torrent.hash),
                        # NewznabTorznabAttr(name="guid", value=torrent.hash),
                        NewznabTorznabAttr(name="seeders", value=str(rarbg_item.seeds)),
                        # NewznabTorznabAttr(name="peers", value=str(torrent.peers)),
                        NewznabTorznabAttr(name="leechers", value=str(rarbg_item.leechers)),
                        NewznabTorznabAttr(name="category", value="5000"),  # Hardcoded for now
                        NewznabTorznabAttr(name="language", value=rarbg_item.language),
                        # NewznabTorznabAttr(name="downloadvolumefactor", value="0"),
                        NewznabTorznabAttr(name="uploadvolumefactor", value="1"),
                        NewznabTorznabAttr(name="uploader", value=rarbg_item.uploader),
                        # *[
                        #     NewznabTorznabAttr(name="tag", value=tag)
                        #     for tag in rarbg_item.tags
                        # ]
                        # Tags
                        # NewznabTorznabAttr(name="tag", value=torrent.type),
                        # NewznabTorznabAttr(name="tag", value=torrent.quality),
                        # NewznabTorznabAttr(name="tag", value=torrent.is_repack),
                        # NewznabTorznabAttr(name="tag", value=torrent.video_codec),
                        # NewznabTorznabAttr(name="tag", value=torrent.audio_channels),
                    ]
                ))

        logger.info("Found `%d` torrents", len(items))
        result = RssResult(
            channel=NewznabChannel(
                title="Rarbg",
                description="RarBG site",
                link=RarbgClient.base_url,
                item=items
            )
        )
        return self._response(result)

    async def get_capabilities(self):
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
                    "default": "20",
                    "max": "20"
                },
                "searching": {
                    "search": {
                        "available": "yes",
                        "supportedParams": "q"
                    },
                    "tv_search": {
                        "available": "yes",
                        "supportedParams": "q,season,ep"
                    },
                    "movie_search": {
                        "available": "yes",
                        "supportedParams": "q"
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
            })

        return self._response(result)

