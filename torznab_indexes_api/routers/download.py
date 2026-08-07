from httpx import AsyncClient

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import RedirectResponse

from torznab_indexes_api.services.rarbg_service import RarbgService
from torznab_indexes_api.services.yts_service import YTSService
from torznab_indexes_api.services.tgx_service import TGxService

SERVICE_MAP = {
    'rarbg': RarbgService(),
    'yts': YTSService(),
    'tgx': TGxService(),
}

router = APIRouter()


@router.get("/{torrent_tag}/{file_link:path}",
            name="download",
            responses={
                200: {
                    "content": {
                        "application/x-bittorrent": {}
                    },
                    "description": "Torrent file",
                }
            }, )
async def download_torrent(torrent_tag: str, file_link: str):
    if torrent_tag not in SERVICE_MAP:
        raise HTTPException(
            status_code=404,
        )
    service = SERVICE_MAP[torrent_tag]
    return RedirectResponse(
        url=await service.get_magnet_link(file_link),
        status_code=302
    )