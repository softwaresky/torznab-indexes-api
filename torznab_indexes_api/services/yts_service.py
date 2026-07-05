import logging

from torznab_indexes_api.core.clients.yts_client import YTSClient
from torznab_indexes_api.schemas.torznab_schemas import (
    RssResult, NewznabGuid, NewznabItem, NewznabChannel, NewznabEnclosure, NewznabTorznabAttr, SearchParams, MovieSearchParams
)
from torznab_indexes_api.schemas.yts_schemas import YTSListMoviesRequestSchema
from torznab_indexes_api.services.base_service import BaseService

logger = logging.getLogger(__name__)

class YTSService(BaseService):

    async def search(self, request_params: SearchParams) -> str:
        logger.info("Search with search params: `%s`", request_params)
        return await self._generic_search(page=request_params.page, limit=request_params.limit, search_terms=request_params.query)

    async def movie_search(self, request_params: MovieSearchParams) -> str:
        logger.info("Search with search params: `%s`", request_params)
        search_terms = request_params.imdbid or request_params.query
        return await self._generic_search(page=request_params.page, limit=request_params.limit, search_terms=search_terms)

    async def _generic_search(self, page: int, limit: int, search_terms: str | None = None) -> str:
        request_yts = YTSListMoviesRequestSchema(query_term=search_terms, page=page, limit=limit)
        items = []
        async with YTSClient() as yts_client:
            async for movie in yts_client.list_movies(request_schema=request_yts):

                for torrent in movie.torrents:
                    if not movie.ptn_validate(season=None, episode=None):
                        continue

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
                        category=f"{torrent.category_id}",
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
                            NewznabTorznabAttr(name="category", value=f"{torrent.category_id}"),
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
