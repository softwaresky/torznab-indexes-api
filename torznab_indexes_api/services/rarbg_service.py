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


    async def get_magnet_link(self, torrent_id: str) -> str:
        async with RarbgClient() as client:
            data = await client.torrent_detail(detail_url=torrent_id)
            return data.get("magnet_link") or ""


    async def _generic_search(
            self, request_params: SearchParams | TvSearchParams | MovieSearchParams,
            search_mode: Literal["tv", "movies", "search", "torrents"] = "torrents",
            categories: list[str] = None,
            search_season: int | None = None,
            search_episode: int  | None = None
    ) -> str:
        items = []

        # parts = []
        # if request_params.query:
        #     parts.append(request_params.query)

        # if search_season:
        #     parts.append(f"S{search_season:02d}")
        #
        # if search_episode:
        #     parts.append(f"E{search_episode:02d}")

        async with RarbgClient() as client:
            async for rarbg_item in client.fetch_data(page=request_params.page, search_terms=request_params.query, search_mode=search_mode, categories=categories):

                # TODO: Until this is done https://github.com/softwaresky/torznab-indexes-api/issues/11
                # if not rarbg_item.ptn_validate(season=search_season, episode=search_episode):
                #     continue

                torrent_url = urljoin(client.base_url, rarbg_item.file_link)
                release_url =  urljoin(self.host_base_url, f"/download/rarbg/{rarbg_item.file_link}")
                tv_attrs = []
                if season := rarbg_item.ptn_data.season:
                    tv_attrs.append(
                        NewznabTorznabAttr(name="season", value=str(season))
                    )
                if episode := rarbg_item.ptn_data.episode:
                    tv_attrs.append(
                        NewznabTorznabAttr(name="episode", value=str(episode))
                    )
                if rarbg_item.language:
                    tv_attrs.append(NewznabTorznabAttr(name="language", value=rarbg_item.language))

                items.append(NewznabItem(
                    title=f"{rarbg_item.release_name or rarbg_item.file}",
                    guid=NewznabGuid(
                        title=torrent_url
                    ),
                    link=torrent_url,
                    comments=torrent_url,
                    pubDate=rarbg_item.added.strftime("%a, %d %b %Y %H:%M:%S %z"),
                    description="",
                    category=f"{rarbg_item.category_id}",
                    enclosure=NewznabEnclosure(
                        url=release_url,
                        type="application/x-bittorrent"
                    ),
                    attrs=[
                        NewznabTorznabAttr(name="size", value=str(rarbg_item.size_bytes)),
                        NewznabTorznabAttr(name="seeders", value=str(rarbg_item.seeds)),
                        NewznabTorznabAttr(name="leechers", value=str(rarbg_item.leechers)),
                        NewznabTorznabAttr(name="category", value=f"{rarbg_item.category_id}"),  # Hardcoded for now
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

