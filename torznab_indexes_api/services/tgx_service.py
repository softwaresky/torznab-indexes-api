import logging
from typing import Type
from torznab_indexes_api.core.clients.tgx_client import TGxClient
from torznab_indexes_api.schemas.torznab_schemas import (
    RssResult, NewznabGuid, NewznabItem, NewznabChannel, NewznabEnclosure, NewznabTorznabAttr
)
from torznab_indexes_api.schemas.tgx_schemas import (
    TGxRequestSchema, TgxItemSchema, AllParamsSchemas, FunctionType
)
from torznab_indexes_api.services.base_service import BaseService

logger = logging.getLogger(__name__)


class TGxService(BaseService):

    async def search(self, request_schema: TGxRequestSchema) -> str:

        logger.info("Search with search params: `%s`", request_schema)


        items = []
        async with TGxClient() as tgx_client:
            async for tgx_item in tgx_client.fetch_data(request_schema=request_schema):
                torrent_url = tgx_client.get_torrent_url(pk=tgx_item.primary_key, title=tgx_item.name)
                # download_url = tgx_client.get_download_url(info_hash=tgx_item.hash, title=tgx_item.name)
                magnet_link = tgx_item.get_magnet_link(
                    trackers=[tgx_client.base_url, "http://itorrents.org"]
                )
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
                        title=torrent_url
                    ),
                    link=magnet_link,
                    comments=torrent_url,
                    pubDate=tgx_item.added.strftime("%a, %d %b %Y %H:%M:%S %z"),
                    description=f"Uploader: {tgx_item.uploader}",
                    category=tgx_item.category,
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
                              NewznabTorznabAttr(name="category", value="5000"),  # Hardcoded for now
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
