import asyncio
import logging
import json

from urllib.parse import urljoin
from enum import Enum, StrEnum
from typing import AsyncGenerator
from functools import lru_cache

from httpx import TimeoutException as HttpxTimeoutError
from bs4 import BeautifulSoup, Tag

from torznab_indexes_api.core.clients.base import Base
from torznab_indexes_api.core.utils import to_kebab
from torznab_indexes_api.schemas import CategoryEnum

logger = logging.getLogger(__name__)


class OptionType(Enum):
    category = "category"
    keywords = "keywords"


class TGxClientOld(Base):
    name = "tgx"
    base_url = "https://torrentgalaxy.one"

    def __init__(self):
        super().__init__()
        self._main_content = ""

    async def get_proxies(self) -> AsyncGenerator[str, None]:
        content = ""
        try:
            content = await self._request("get", url="https://proxygalaxy.me/")
        except HttpxTimeoutError:
            pass

        soup = BeautifulSoup(content, "html.parser")

        pgxtron_div = soup.find("div", {"id": "pgxtron"})
        tables = pgxtron_div.find_all("table")
        for table_el_ in tables:
            table_row = table_el_.find_next("tr").find_all("td")
            if len(table_row) >= 2 and "online" in table_row[1].text.strip().lower():
                yield table_row[0].find_next("a").attrs["href"]

    async def get_content(self, url: str, params: dict | None = None) -> str:

        keep_running = True
        while keep_running:

            try:
                return await self._request(method="GET", url=urljoin(self.base_url, url),
                                           params=params)
            except HttpxTimeoutError:
                keep_running = False
                # try:
                #     proxy_url = await anext(self.get_proxies(), None)
                #     if proxy_url:
                #         self.base_url = proxy_url
                #     else:
                #         keep_running = False
                # except StopIteration:
                #     keep_running = False

        # logger.info("Request with Playwright")
        # try:
        #     content = await self._reqeust_playwright(url="torrents.php", params=params)
        # except PlaywrightTimeoutError:
        #     content = ""

        return ""

    async def _fetch_options(self, opt_type: OptionType) -> AsyncGenerator:

        if not self._main_content:
            self._main_content = await self.get_content(url="get-posts/keywords")

        soup = BeautifulSoup(self._main_content, "html.parser")
        category_blok = soup.find("div", {"id": "intblockslide"})
        if not category_blok:
            return

        for label_el in category_blok.find_all("label"):
            link = label_el.find("a")
            if isinstance(link, Tag):
                data = self.parse_query(link.attrs["href"])
                print(link.attrs["href"])
                data["name"] = label_el.text.strip()
                if opt_type == OptionType.category and {"cat"} & data.keys():
                    yield data
                elif opt_type == OptionType.keywords and {"genres[]"} & data.keys():
                    yield data

    async def fetch_categories(self, *args, **kwargs) -> AsyncGenerator:
        async for item_ in self._fetch_options(opt_type=OptionType.category):
            yield item_

    async def fetch_genres(self, *args, **kwargs) -> AsyncGenerator:
        async for item_ in self._fetch_options(opt_type=OptionType.keywords):
            yield item_

    @staticmethod
    def parse_element(element: Tag):
        value = element.text.strip()

        if value:
            return value.replace("\xa0", "")

        results = []
        for sub_el_ in element.children:
            if not isinstance(sub_el_, Tag):
                continue
            for attr_name in ["href", "title"]:
                if attr_name in sub_el_.attrs:
                    results.append(sub_el_.attrs[attr_name].strip())

        if not results:
            return None
        elif len(results) == 1:
            return results.pop()
        else:
            return results

    @lru_cache(maxsize=1)
    async def category_map(self) -> dict:
        results = {}
        async for cat_ in self.fetch_categories():
            name = cat_["name"].strip().replace(" ", "")
            results[name] = cat_["cat"]
        return results

    async def fetch_data_old(
            self, search_terms: str, sort: str = "seeders", order="desc",
            page: int = 0, recursive: bool = False
    ) -> AsyncGenerator:

        params = {
            # "search": search_terms
        }
        if sort:
            params["sort"] = sort
        if order:
            params["order"] = order
        if page:
            params["page"] = page

        content = await self.get_content(url=f"get-posts/keywords:{search_terms}", params=params)
        self._main_content = content
        # category_map = await self.category_map()

        if content:
            soup = BeautifulSoup(content.encode("utf-8"), 'html.parser')

            table_el = soup.find("div", {"class": "tgxtable"})
            if not table_el:
                # table_el

                return

            table_header_el = table_el.find(
                "div", {"class": "tgxtablehead"}).find_all(
                "div", {"class": "tgxtablecell"}
            )

            table_header = []

            for el_ in table_header_el:
                table_header.append(self.parse_element(el_).lower())

            table_rows = table_el.find_all("div", {"class": "tgxtablerow"})
            for row_ in table_rows:
                row_items = row_.find_all("div", {"class": "tgxtablecell"})
                row_values = []
                for row_el_ in row_items:
                    value = self.parse_element(row_el_)
                    row_values.append(value)

                data = dict(zip(table_header, row_values))
                # category_key = data["type"].replace(":", "-").strip().replace(" ", "")
                # data["category"] = category_map[category_key]

                rel_url = row_.find_next("div", {"id": "click"}).find_next("a").get("href")
                data["torrent_url"] = urljoin(self.base_url, rel_url)

                yield data

            page_links = soup.find(
                "nav", {"aria-label": "pages"}).find(
                "ul", {"id": "pager"}).find_all("a", {"class": "page-link"})

            if len(page_links) > 1 and recursive:
                next_page_url = [
                    page_el.attrs["href"] for page_el in page_links
                    if page_el.text == "Next" and page_el.attrs.get("tabindex") != "-1"
                ]
                if next_page_url:
                    next_page_url = next_page_url.pop()

                    url_params = self.parse_query(next_page_url)
                    if {"page"} & url_params.keys():
                        next_page = int(url_params["page"])
                        if page > 0:
                            async for data in self.fetch_data_old(
                                    search_terms=search_terms,
                                    sort=sort,
                                    order=order,
                                    page=next_page
                            ):
                                category_key = data["type"].replace(":", "-").strip().replace(" ",
                                                                                              "")
                                # data["category"] = category_map[category_key]
                                yield data


class TGxClient(Base):
    name = "tgx"
    base_url = "https://torrentgalaxy.one"

    async def parse_torrent_data(self, torrent_url: str) -> dict:
        results = {}
        content = await self._request(method="GET", url=torrent_url)
        if content:
            soup = BeautifulSoup(content.encode("utf-8"), 'html.parser')
            labels = ["category", "language", "added", "info hash", "checked by"]
            torrent_tables = soup.find_all("div", {"class": "torrentpagetable limitwidth txlight"})
            for table_el in torrent_tables:
                for table_row_el in table_el.find_all_next("div", {"class": "tprow"}):
                    row_cells = table_row_el.find_all_next("div", {"class": "tpcell"})

                    for label in labels:
                        if label in row_cells[0].text.strip().lower():
                            results[label] = row_cells[1].text.strip()

            magnet_info = soup.find_all("div", {"id": "covercell", "class": "tpcell"})
            links = []
            for table_el in magnet_info:
                for a_el in table_el.find_all("a"):
                    links.append(a_el.attrs["href"])

            magnet = [
                link for link in links if link.startswith("magnet:")
            ]
            if magnet:
                magnet = magnet.pop()
                results["magnet"] = magnet

        return results

    async def _fetch_data_json(
            self,
            url: str,
            page: int = 0,
            recursive: bool = False,
    ) -> AsyncGenerator:

        params = {}
        if page:
            params["page"] = page

        content = await self._request(
            method="GET",
            url=url,
            params=params
        )
        if content:
            try:
                json_data: dict = json.loads(content)
            except json.JSONDecodeError:
                raise Exception("No json structure")

            for item in json_data.get("results", []):
                yield item

            if recursive:
                next_link = json_data.get("links", {}).get("next")
                if next_link:
                    page += 1
                    async for item in self._fetch_data_json(url=url, page=page, recursive=recursive):
                        yield item

    async def _get_post_details(self, pk: str, n: str, *args, **kwargs) -> dict:
        if not pk or not n:
            return {}
        return await self.parse_torrent_data(torrent_url=f"post-detail/{pk}/{to_kebab(n)}/")


    async def fetch_data(
            self,
            search_terms: str,
            category_enum: CategoryEnum | None = None,
            page: int = 0,
            recursive: bool = False
    ) -> AsyncGenerator:

        results = []
        tasks = []

        filters = []
        if search_terms:
            filters.append(f"keywords:{search_terms}")

        if category_enum:
            filters.append(f"category:{category_enum.value}")

        url = f"get-posts/{':'.join(filters)}:format:json"

        async for item in self._fetch_data_json(url=url, page=page, recursive=recursive):
            tasks.append(asyncio.create_task(self._get_post_details(**item)))
            results.append(item)

        items_details = await asyncio.gather(*tasks)

        for item, item_detail in zip(results, items_details):
            item.update({
                key: item_detail[key]
                for key in item_detail.keys() - item.keys()
            })
            yield item


