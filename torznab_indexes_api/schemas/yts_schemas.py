from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator
from torznab_indexes_api.core.types import EnsureDateTime
from torznab_indexes_api.schemas import merge_models
from torznab_indexes_api.schemas.torznab_schemas import  SearchSchema, MovieSearchSchema, BaseRequestSchema

class FunctionType(str, Enum):
    caps = "caps"
    search = "search"
    movie = "movie"


class AllParamsSchemas(merge_models(
    "AllParams",
    SearchSchema, MovieSearchSchema)):
    pass


class YTSRequestSchema(BaseRequestSchema):
    search_params: MovieSearchSchema | SearchSchema |  None = Field(
        default=None, union_mode="left_to_right"
    )

    def search_terms(self) -> str:
        query: str | None = getattr(self.search_params, "query", "")
        imdb_id: str | None = getattr(self.search_params, "imdbid", "")

        return imdb_id or query


class YTSMovieDetailsRequestSchema(BaseModel):
    movie_id: str | None = Field(default=None, description="Integer (Unsigned) The YTS ID of the movie")
    imdb_id: str | None = Field(default=None, description="Integer (Unsigned) The IMDB ID of the movie")
    with_images: str | None = None
    with_cast: str | None = None

    @model_validator(mode="before")
    @classmethod
    def model_validator_(cls, values: dict[str, Any]) -> dict[str, Any]:
        if values.get("imdb_id") or values.get("movie_id"):
            return values
        raise ValueError("Either imdb_id or movie_id must be provided")


class YTSListMoviesRequestSchema(BaseModel):
    limit: int = Field(default=20,
                       description="Integer between 1 - 50 (inclusive)	20	The limit of results per page that has been set")
    page: int = Field(default=1,
                      description="Integer (Unsigned)	1	Used to see the next page of movies, eg limit=15 and page=2 will show you movies 15-30")
    quality: str = Field(default="",
                         description="String (480p, 720p, 1080p, 1080p.x265, 2160p, 3D)	All	Used to filter by a given quality")
    minimum_rating: int = Field(default=0, ge=0, le=9,
                                description="Integer between 0 - 9 (inclusive)	0	Used to filter movie by a given minimum IMDb rating")
    query_term: str = Field(default="",
                            description="String	0	Used for movie search, matching on: Movie Title/IMDb Code, Actor Name/IMDb Code, Director Name/IMDb Code")
    genre: str = Field(default="",
                       description="String	All	Used to filter by a given genre (See http://www.imdb.com/genre/ for full list")
    sort_by: str = Field(default="seeds",
                         description="String (title, year, rating, peers, seeds, download_count, like_count, date_added) date_added	Sorts the results by chosen value")
    order_by: str = Field(default="desc",
                          description="String (desc, asc)	desc	Orders the results by either Ascending or Descending order")
    with_rt_ratings: bool = Field(default=False,
                                  description="Boolean	false	Returns the list with the Rotten Tomatoes rating included")


class YTSResponseTorrentSchema(BaseModel):
    url: str
    hash: str
    quality: str
    type: str
    is_repack: str
    video_codec: str
    bit_depth: str
    audio_channels: str
    seeds: int
    peers: int
    size: str
    size_bytes: int
    date_uploaded: EnsureDateTime
    date_uploaded_unix: int

    @property
    def leechers(self) -> int:
        return self.seeds - self.peers


class YTSResponseMovieSchema(BaseModel):
    id: int
    url: str
    imdb_code: str
    title: str
    title_english: str
    title_long: str
    slug: str
    year: int
    rating: float
    runtime: int
    genres: list[str]
    summary: str | None = None
    description_full: str
    synopsis: str | None = None
    yt_trailer_code: str
    language: str
    mpa_rating: str
    background_image: str
    background_image_original: str
    small_cover_image: str
    medium_cover_image: str
    large_cover_image: str
    state: str | None = None
    torrents: list[YTSResponseTorrentSchema]
    date_uploaded: EnsureDateTime | None = None
    date_uploaded_unix: int | None = None
