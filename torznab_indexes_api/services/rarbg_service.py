import logging
from typing import Literal
from urllib.parse import urljoin
from torznab_indexes_api.core.clients.rarbg_client import RarbgClient
from torznab_indexes_api.services.base_service import BaseService
from torznab_indexes_api.schemas.torznab_schemas import (
    RssResult, NewznabGuid, NewznabItem, NewznabChannel, NewznabEnclosure, NewznabTorznabAttr, RssCapabilitiesSchema,
    SearchParams, TvSearchParams, MovieSearchParams
)
logger = logging.getLogger(__name__)


class RarbgService(BaseService):

    async def search(self, request_params: SearchParams) -> str:
        logger.info("Search with search params: `%s`", request_params)
        return await self._generic_search(
            request_params=request_params, search_mode="search" if request_params.query else "torrents",  categories=["tv", "movies"]
        )

    async def tv_search(self, request_params: TvSearchParams) -> str:
        logger.info("Search with search params: `%s`", request_params)
        return await self._generic_search(
            request_params=request_params, search_mode="tv", categories=["tv"], search_season=request_params.season, search_episode=request_params.episode
        )

    async def movie_search(self, request_params: MovieSearchParams) -> str:
        logger.info("Search with search params: `%s`", request_params)
        return await self._generic_search(request_params=request_params, search_mode="movies", categories=["movies"])


    async def _generic_search(
            self, request_params: SearchParams | TvSearchParams | MovieSearchParams,
            search_mode: Literal["tv", "movies", "search", "torrents"] = "torrents",
            categories: list[str] = None,
            search_season: int | str | None = None,
            search_episode: int | str | None = None
    ) -> str:
        items = []
        async with RarbgClient() as client:
            async for rarbg_item in client.fetch_data(page=request_params.page, search_terms=request_params.query, search_mode=search_mode, categories=categories):
                if not rarbg_item.ptn_validate(season=search_season, episode=search_episode):
                    continue

                torrent_url = urljoin(client.base_url, rarbg_item.file_link)
                tv_attrs = []
                if season := rarbg_item.ptn_data.season:
                    tv_attrs.append(
                        NewznabTorznabAttr(name="season", value=str(season))
                    )
                if episode := rarbg_item.ptn_data.episode:
                    tv_attrs.append(
                        NewznabTorznabAttr(name="episode", value=str(episode))
                    )
                items.append(NewznabItem(
                    title=f"{rarbg_item.release_name or rarbg_item.file}",
                    guid=NewznabGuid(
                        title=torrent_url
                    ),
                    link=rarbg_item.magnet_link,
                    comments=torrent_url,
                    pubDate=rarbg_item.added.strftime("%a, %d %b %Y %H:%M:%S %z"),
                    description="",
                    category=f"{rarbg_item.category_id}",
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
                        NewznabTorznabAttr(name="category", value=f"{rarbg_item.category_id}"),  # Hardcoded for now
                        NewznabTorznabAttr(name="language", value=rarbg_item.language),
                        # NewznabTorznabAttr(name="downloadvolumefactor", value="0"),
                        NewznabTorznabAttr(name="uploadvolumefactor", value="1"),
                        NewznabTorznabAttr(name="uploader", value=rarbg_item.uploader),
                    ] + tv_attrs
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
                    "categories": self.get_categories(),
                },
            })

        return self._response(result)

