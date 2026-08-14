import json
import logging
from hashlib import md5
from typing import AsyncGenerator

from urllib.parse import urlparse, parse_qs

from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
    retry_if_exception_type,
    retry_if_result,
)

from httpx import AsyncClient, Response, HTTPError, TimeoutException, ConnectError
from torznab_indexes_api.core.cache import get_request_cache

logger = logging.getLogger(__name__)


class BaseClient:
    name: str
    base_url: str

    def __init__(self):
        self._session: AsyncClient | None = None


    async def _create_session(self):
        self._session = AsyncClient(base_url=self.base_url, timeout=30)

    @staticmethod
    def _build_cache_key(method: str,url: str,**kwargs) -> str:
        data = {
            "method": method.upper(),
            "url": url,
            "params": kwargs.get("params"),
            "json": kwargs.get("json"),
            "content": kwargs.get("content"),
        }

        serialized = json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )
        return md5(serialized.encode("utf-8")).hexdigest()

    async def _request(self, method: str, url: str, **kwargs) -> str:

        request_key = self._build_cache_key(method, url, **kwargs)
        cached = await get_request_cache().get(request_key=request_key)
        if cached:
            return cached

        response = await self._request_and_retry(method, url, **kwargs)

        if response.is_success:
            await get_request_cache().set(request_key=request_key, value=response.text)
            return response.text
        else:
            try:
                response.raise_for_status()
            except HTTPError:
                logger.error(response.text)

        return ""

    # Define the conditions for retrying based on HTTP status codes
    @staticmethod
    def is_retryable_status_code(response: Response):
        return response.status_code in [500, 503, 504]

    @retry(
        retry=(
                retry_if_result(is_retryable_status_code)
                | retry_if_exception_type((TimeoutException, ConnectError))
        ),
        stop=stop_after_attempt(10),
        wait=wait_fixed(5),
    )
    async def _request_and_retry(self, method: str, url: str, **kwargs) -> Response:
        return await self._session.request(method, url, **kwargs)


    async def _request_playwright(self, url: str, params: dict | None = None, **kwargs) -> str:
        # async with async_playwright() as p:
        #     browser = await p.chromium.launch(headless=True)
        #     page = await browser.new_page()
        #     await page.goto(f"{urljoin(self.base_url, url)}?{urlencode(query=params)}")
        #     await page.locator("//div[@class='tgxtable']").wait_for(timeout=120.0, state="visible")
        #     result = await page.content()
        #     await browser.close()
        #
        # return result
        pass

    async def close(self):
        if self._session:
            await self._session.aclose()

    async def __aenter__(self):
        await self._create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @staticmethod
    def parse_query(url: str) -> dict:
        if not url:
            return {}

        parsed_url = urlparse(url)
        return {
            key_: value_.pop()
            for key_, value_ in parse_qs(parsed_url.query).items()
            if value_
        }

    async def fetch_data(self, *args, **kwargs) -> AsyncGenerator:
        raise NotImplementedError
