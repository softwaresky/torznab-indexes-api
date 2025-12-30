import logging

from torznab_indexes_api.core.clients.yts_client import YTSClient
from torznab_indexes_api.schemas.torznab_schemas import (
    RssResult, NewznabGuid, NewznabItem, NewznabChannel, NewznabEnclosure, NewznabTorznabAttr
)
from torznab_indexes_api.schemas.yts_schemas import YTSRequestSchema, YTSListMoviesRequestSchema
from torznab_indexes_api.services.base_service import BaseService

logger = logging.getLogger(__name__)

class YTSService(BaseService):

    async def search(self, request_schema: YTSRequestSchema) -> str:

        logger.info("Search with search params: `%s`", request_schema)


        request_yts_client = YTSListMoviesRequestSchema(query_term=request_schema.search_terms())
        items = []
        async with YTSClient() as yts_client:
            async for movie in yts_client.list_movies(request_schema=request_yts_client):

                for torrent in movie.torrents:
                    # download_url = tgx_client.get_download_url(info_hash=tgx_item.hash, title=tgx_item.name)
                    magnet_link = torrent.url
                    items.append(NewznabItem(
                        title=f"{movie.title_long} {torrent.quality} {torrent.type} {torrent.audio_channels} {torrent.bit_depth}Bit {torrent.video_codec}",
                        guid=NewznabGuid(
                            title=torrent.url
                        ),
                        link=magnet_link,
                        comments=torrent.url,
                        pubDate=torrent.date_uploaded.strftime("%a, %d %b %Y %H:%M:%S %z"),
                        description=movie.description_full,
                        category="Movies",
                        enclosure=NewznabEnclosure(
                            url=magnet_link,
                            type="application/x-bittorrent"
                        ),
                        attrs=[
                            NewznabTorznabAttr(name="size", value=str(torrent.size_bytes)),
                            NewznabTorznabAttr(name="infohash", value=torrent.hash),
                            NewznabTorznabAttr(name="guid", value=torrent.hash),
                            NewznabTorznabAttr(name="seeders", value=str(torrent.seeds)),
                            NewznabTorznabAttr(name="peers", value=str(torrent.peers)),
                            NewznabTorznabAttr(name="leechers", value=str(torrent.leechers)),
                            NewznabTorznabAttr(name="category", value="5000"),  # Hardcoded for now
                            NewznabTorznabAttr(name="language", value=movie.language),
                            NewznabTorznabAttr(name="downloadvolumefactor", value="0"),
                            NewznabTorznabAttr(name="uploadvolumefactor", value="1"),

                            NewznabTorznabAttr(name="resolution", value=torrent.quality),
                            NewznabTorznabAttr(name="codec", value=torrent.type),

                            # Tags
                            NewznabTorznabAttr(name="tag", value=torrent.type),
                            NewznabTorznabAttr(name="tag", value=torrent.quality),
                            NewznabTorznabAttr(name="tag", value=torrent.is_repack),
                            NewznabTorznabAttr(name="tag", value=torrent.video_codec),
                            NewznabTorznabAttr(name="tag", value=torrent.audio_channels),
                        ]
                    ))

        logger.info("Found `%d` torrents", len(items))
        result = RssResult(
            channel=NewznabChannel(
                title="YTS",
                description="YTS site",
                link=YTSClient.base_url,
                item=items
            )
        )
        return self._response(result)
