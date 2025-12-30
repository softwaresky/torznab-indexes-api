
import logging
import json

from typing import AsyncGenerator

from pydantic import ValidationError

from torznab_indexes_api.core.clients.base_client import BaseClient
from torznab_indexes_api.schemas.yts_schemas import YTSListMoviesRequestSchema, YTSResponseMovieSchema, YTSMovieDetailsRequestSchema


logger = logging.getLogger(__name__)


class YTSClient(BaseClient):
    """YTS client is implemented based on this restful API
    https://yts.lt/api
    """

    base_url = "https://yts.lt/api/v2"


    async def list_movies(self, request_schema: YTSListMoviesRequestSchema) -> AsyncGenerator[YTSResponseMovieSchema, None]:
        params = request_schema.model_dump(exclude_none=True, exclude_unset=True)
        response_str = await self._request(method="GET", url="list_movies.json", params=params)
        if response_str:
            response_data = json.loads(response_str)
            for movie in response_data.get("data", {}).get("movies", []):
                try:
                    yield YTSResponseMovieSchema.model_validate(movie)
                except ValidationError as err:
                    logger.error("Failed validation on `%s`. Data: `%s`",
                                 YTSResponseMovieSchema.__class__.__name__,
                                 err.json(include_url=False)
                                 )


    async def get_movie_detail(self, request_schema: YTSMovieDetailsRequestSchema) -> YTSResponseMovieSchema | None:
        params = request_schema.model_dump(exclude_none=True, exclude_unset=True)
        response_str = await self._request(method="GET", url="movie_details.json", params=params)
        if response_str:
            response_data = json.loads(response_str)
            return YTSResponseMovieSchema.model_validate(response_data.get("data", {}).get("movie", {}))
        return None
