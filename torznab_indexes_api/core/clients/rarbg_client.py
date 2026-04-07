import asyncio
import logging
from typing import AsyncGenerator, Any
from bs4 import BeautifulSoup
from pydantic import ValidationError

from torznab_indexes_api.core.clients.base_client import BaseClient
from torznab_indexes_api.schemas.rarbg_schemas import RarbgRequestSchema, RarbgItemSchema

logger = logging.getLogger(__name__)

class RarbgClient(BaseClient):
    base_url = "https://rargb.to"

    @staticmethod
    def _parse_response(response_str: str) -> list[dict[str, Any]]:
        results = []
        soup = BeautifulSoup(response_str, "html.parser")

        table = soup.find("table", class_="lista2t")

        header_row = table.find("tr")
        headers = []

        for th in header_row.find_all("td"):
            text = th.get_text(strip=True).lower().rstrip(".")
            headers.append(text)

        rows = table.find_all("tr")[1:]  # skip header row

        for row in rows:
            cols = row.find_all("td")

            if len(cols) != len(headers):
                continue

            row_data = {}

            for i in range(len(headers)):
                col = cols[i]

                if headers[i] == "file":
                    a_tag = col.find("a")
                    row_data["file"] = a_tag.get_text(strip=True) if a_tag else None
                    row_data["file_link"] = a_tag.get("href") if a_tag else None

                elif headers[i] == "category":
                    links = col.find_all("a")
                    row_data["category"] = " ".join(a.get_text(strip=True) for a in links)

                else:
                    row_data[headers[i]] = col.get_text(strip=True)

            results.append(row_data)

        return results


    async def get_magnet(self, detail_url: str) -> str | None:
        headers = {"User-Agent": "Mozilla/5.0"}
        response_str = await self._request(method="GET", url=detail_url, headers=headers)
        soup = BeautifulSoup(response_str, "html.parser")

        # most torrent sites have magnet link like this:
        magnet_tag = soup.find("a", href=lambda x: x and x.startswith("magnet:"))

        if magnet_tag:
            return magnet_tag["href"]

        return None


    async def torrent_detail(self, detail_url: str) -> dict[str, Any]:
        response_str = await self._request(method="GET", url=detail_url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response_str, "html.parser")

        data = {}
        magnet_tag = soup.find("a", href=lambda x: x and x.startswith("magnet:"))

        if magnet_tag:
            data["magnet_link"] = magnet_tag["href"]

        rows = soup.select("tbody tr")

        for row in rows:
            header = row.find("td", class_="header2")
            value = row.find_all("td", class_="lista")

            if not header or len(value) < 1:
                continue

            key = header.get_text(strip=True).replace(":", "").lower()
            val_td = value[0]

            if key == "tags":
                tags = [a.get_text(strip=True) for a in val_td.find_all("a")]
                data["tags"] = tags

            elif key == "release name":
                data["release_name"] = val_td.get_text(strip=True)

            elif key == "language":
                data["language"] = val_td.get_text(strip=True)

        return data

    async def fetch_data(self, request_schema: RarbgRequestSchema) -> AsyncGenerator[RarbgItemSchema, None]:
        response_str = await self._request(
            method="GET",
            url=f"search/{request_schema.search_params.page}",
            headers={ "User-Agent": "Mozilla/5.0" },
            params={ "search": request_schema.search_terms()},
        )
        items = self._parse_response(response_str)
        torrents_detail = await asyncio.gather(*[
            self.torrent_detail(detail_url=item["file_link"]) for item in items
        ])
        for item, torrent_detail in zip(items, torrents_detail):
            try:
                yield RarbgItemSchema.model_validate(item | torrent_detail)
            except ValidationError as err:
                logger.error("Failed validation on `%s`. Data: `%s`",
                             RarbgItemSchema.__class__.__name__,
                             err.json(include_url=False)
                             )

