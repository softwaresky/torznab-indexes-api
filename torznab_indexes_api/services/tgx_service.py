import logging
from torznab_indexes_api.core.clients.tgx_client import TGxClient
from torznab_indexes_api.schemas.torznab_schemas import (
    RssResult, NewznabGuid, NewznabItem, NewznabChannel, NewznabEnclosure, NewznabTorznabAttr, SearchParams, TvSearchParams, MovieSearchParams
)
from torznab_indexes_api.services.base_service import BaseService

logger = logging.getLogger(__name__)


class TGxService(BaseService):


    async def search(self, request_params: SearchParams) -> str:
        logger.info("Search with search params: `%s`", request_params)
        query = request_params.query or ""
        filters = []
        if query:
            filters.append(f"keywords:{query.strip()}")
        else:
            filters.append("category:TV")
            filters.append("category:Movies")

        return await self._generic_search(page=request_params.page, search_terms=":".join(filters))

    async def tv_search(self, request_params: TvSearchParams) -> str:
        logger.info("Search with search params: `%s`", request_params)
        query = request_params.query or ""

        filters = [
            "category:TV"
        ]
        query_parts = query.split()
        imdb_id = request_params.imdbid
        if isinstance(request_params.season, int):
            season_str = f"s{request_params.season:0>2d}"
            if season_str not in query_parts:
                query += f" {season_str}"
        if isinstance(request_params.episode, int):
            eps_str = f"e{request_params.episode:0>2d}"
            if eps_str not in query_parts:
                query += f" {eps_str}"

        keywords = imdb_id or query

        if keywords:
            filters.append(f"keywords:{keywords}")

        return await self._generic_search(
            page=request_params.page, search_terms=":".join(filters), search_season=request_params.season, search_episode=request_params.episode
        )

    async def movie_search(self, request_params: MovieSearchParams) -> str:
        logger.info("Search with search params: `%s`", request_params)

        query = request_params.query or ""

        filters = [
            "category:Movies"
        ]
        keywords = request_params.imdbid or query
        if keywords:
            filters.append(f"keywords:{keywords}")

        return await self._generic_search(page=request_params.page, search_terms=":".join(filters))


    async def _generic_search(
            self, page: int, search_terms: str, search_season: int | str | None = None, search_episode: int | str | None = None
    ) -> str:

        items = []
        async with TGxClient() as tgx_client:
            async for tgx_item in tgx_client.fetch_data(page=page, search_terms=search_terms):
                if not tgx_item.ptn_validate(season=search_season, episode=search_episode):
                    continue
                torrent_url = tgx_client.get_torrent_url(pk=tgx_item.primary_key, title=tgx_item.name)
                # download_url = tgx_client.get_download_url(info_hash=tgx_item.hash, title=tgx_item.name)
                magnet_link = tgx_item.get_magnet_link(
                    trackers=[tgx_client.base_url, "http://itorrents.org"]
                )
                tv_attrs = []
                if season := tgx_item.ptn_data.season:
                    tv_attrs.append(
                        NewznabTorznabAttr(name="season", value=str(season))
                    )
                if episode := tgx_item.ptn_data.episode:
                    tv_attrs.append(
                        NewznabTorznabAttr(name="episode", value=str(episode))
                    )
                items.append(NewznabItem(
                    title=tgx_item.name,
                    guid=NewznabGuid(
                        title=torrent_url
                    ),
                    link=magnet_link,
                    comments=torrent_url,
                    pubDate=tgx_item.added.strftime("%a, %d %b %Y %H:%M:%S %z"),
                    description=f"Uploader: {tgx_item.uploader}",
                    category=f"{tgx_item.category_id}",
                    enclosure=NewznabEnclosure(
                        url=magnet_link,
                        type="application/x-bittorrent"
                    ),
                    attrs=[
                              NewznabTorznabAttr(name="size", value=str(tgx_item.size)),
                              NewznabTorznabAttr(name="infohash", value=tgx_item.hash),
                              NewznabTorznabAttr(name="guid", value=tgx_item.hash),
                              NewznabTorznabAttr(name="seeders", value=str(tgx_item.seeders)),
                              NewznabTorznabAttr(name="leechers", value=str(tgx_item.leechers)),
                              NewznabTorznabAttr(name="category", value=f"{tgx_item.category_id}"),
                              NewznabTorznabAttr(name="language", value=tgx_item.language),
                              NewznabTorznabAttr(name="downloadvolumefactor", value="0"),
                              NewznabTorznabAttr(name="uploadvolumefactor", value="1"),
                              NewznabTorznabAttr(name="uploader", value=tgx_item.uploader),
                              NewznabTorznabAttr(name="tags", value=",".join(tgx_item.tags)),
                          ] + tv_attrs
                ))

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
