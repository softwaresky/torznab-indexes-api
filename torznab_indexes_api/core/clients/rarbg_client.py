import logging
from typing import AsyncGenerator, Any, Literal
from bs4 import BeautifulSoup
from pydantic import ValidationError
from httpx import AsyncClient

from torznab_indexes_api.core.config.settings import get_settings
from torznab_indexes_api.core.clients.base_client import BaseClient
from torznab_indexes_api.schemas.rarbg_schemas import RarbgItemSchema

logger = logging.getLogger(__name__)


class RarbgClient(BaseClient):
    base_url = "https://rargb.to"
    flare_solver_url = get_settings().flare_solver_url

    async def _request(self, method: str, url: str, **kwargs) -> str:
        """
        Override the base _request method to route GET requests through FlareSolverr
        to bypass Cloudflare challenges.
        """
        # Construct the full target URL if a relative path is passed
        full_url = f"{self.base_url}/{url.lstrip('/')}" if not url.startswith("http") else url

        payload = {
            "cmd": "request.get",
            "url": full_url,
            "maxTimeout": 60000,
        }

        async with AsyncClient() as client:
            try:
                response = await client.post(
                    self.flare_solver_url,
                    json=payload,
                    timeout=70.0
                )
                response.raise_for_status()
                data = response.json()

                if data.get("status") == "ok":
                    return data["solution"]["response"]
                else:
                    logger.error("FlareSolverr failed to solve challenge: %s", data)
                    raise Exception(f"FlareSolverr error: {data.get('message')}")
            except Exception as e:
                logger.exception("Error communicating with FlareSolverr for URL: %s", full_url)
                raise e

    @staticmethod
    def _parse_response(response_str: str) -> list[dict[str, Any]]:
        results = []
        soup = BeautifulSoup(response_str, "html.parser")

        table = soup.find("table", class_="lista2t")
        if table is None:
            return []

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
        response_str = await self._request(method="GET", url=detail_url)
        soup = BeautifulSoup(response_str, "html.parser")

        magnet_tag = soup.find("a", href=lambda x: x and x.startswith("magnet:"))
        if magnet_tag:
            return magnet_tag["href"]

        return None

    async def torrent_detail(self, detail_url: str) -> dict[str, Any]:
        response_str = await self._request(method="GET", url=detail_url)
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

    async def fetch_data(
            self, page: int, search_terms: str | None = None,
            search_mode: Literal["tv", "movies", "search", "torrents"] = "torrents", categories: list[str] | None = None
    ) -> AsyncGenerator[RarbgItemSchema, None]:
        params: list[tuple[str, str]] = []
        if search_terms:
            params.append(("search", search_terms))
            search_mode = "search"

        for category in categories or []:
            params.append(("category[]", category))

        # Build query string manually if params exist since FlareSolverr takes a plain URL string
        query_path = f"{search_mode}/{page}"
        if params:
            query_string = "&".join([f"{k}={v}" for k, v in params])
            query_path = f"{query_path}?{query_string}"

        response_str = await self._request(
            method="GET",
            url=query_path,
        )

        items = self._parse_response(response_str)
        for item in items:
            try:
                yield RarbgItemSchema.model_validate(item)
            except ValidationError as err:
                logger.error("Failed validation on `%s`. Data: `%s`",
                             RarbgItemSchema.__class__.__name__,
                             err.json(include_url=False)
                             )