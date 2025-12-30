from datetime import datetime
from enum import Enum
from typing import Literal, Annotated

from dateutil import parser, tz
from functools import cached_property

from pydantic import (
    BaseModel, field_validator, Field
)

import PTN

from torznab_indexes_api.core.utils import get_past_date
from torznab_indexes_api.schemas import merge_models
from torznab_indexes_api.schemas.torznab_schemas import TvSearchSchema, MovieSearchSchema, SearchSchema


class FunctionType(str, Enum):
    caps = "caps"
    search = "search"
    tvsearch = "tvsearch"
    movie = "movie"


class AllParamsSchemas(merge_models(
    "AllParams",
    SearchSchema, TvSearchSchema, MovieSearchSchema)):
    pass


class TGxRequestSchema(BaseModel):
    """Torrent Galaxy Request structure
    """

    search_params: TvSearchSchema | MovieSearchSchema | SearchSchema | None = Field(
        default=None, union_mode="left_to_right"
    )

    def search_terms(self) -> str:
        filters = []
        if not self.search_params:
            return ""

        query = self.search_params.query.strip()
        query_parts = query.split()
        imdb_id: str | None = None
        category: str | None = None

        match self.search_params:
            case MovieSearchSchema():
                category = "Movies"
                imdb_id = self.search_params.imdbid
            case TvSearchSchema():
                category = "TV"
                imdb_id = self.search_params.imdbid
                if isinstance(self.search_params.season, int):
                    season_str = f"s{self.search_params.season:0>2d}"
                    if season_str not in query_parts:
                        query += f" {season_str}"
                if isinstance(self.search_params.episode, int):
                    eps_str = f"e{self.search_params.episode:0>2d}"
                    if eps_str not in query_parts:
                        query += f" {eps_str}"

        keywords = imdb_id or query

        if keywords:
            filters.append(f"keywords:{keywords}")

        if not imdb_id and category:
            filters.append(f"category:{category}")

        return ":".join(filters)


class TgxItemSchema(BaseModel):
    primary_key: str = Field(default="", alias="pk")
    category: str = Field(default="", alias="c")
    verified: str = Field(default="", alias="checked by")
    language: str = ""
    name: str = Field(alias="n")
    magnet: str = ""
    rating: str = ""
    uploader: str = Field(default="", alias="u")
    size: int = Field(alias="s")
    comments: int = 0
    views: int = 0
    seeders: int = Field(default=0, alias="se")
    leechers: int = Field(default=0, alias="le")
    added: datetime | None = Field(default=None, alias="a")
    hash: str = Field(default="", alias="h")
    tags: list[str] = Field(default=[], alias="tg")

    @cached_property
    def title_parsed_data(self) -> dict:
        return PTN.parse(self.name)

    @field_validator("verified", mode="before")
    def verified_validator(cls, v) -> str:
        if isinstance(v, str):
            return v.split("\n")[-1].strip()
        return v

    @field_validator("added", mode="before")
    def date_validator(cls, v):
        if isinstance(v, str):
            v = v.split("\n")[0]
            try:
                return parser.parse(v, dayfirst=True).replace(tzinfo=tz.tzlocal())
            except:
                try:
                    return get_past_date(v)
                except ValueError:
                    pass

        return v

    # @computed_field
    # @property
    # def torrent_url(self) -> str:
    #     return f"https://torrentgalaxy.one/post-detail/{self.primary_key}/{to_kebab(self.name)}/"
    #
    #
    # @computed_field
    # @property
    # def download_url(self) -> str:
    #     return f"http://itorrents.org/torrent/{self.hash}?title={self.name}"

    def get_magnet_link(self, trackers: list[str] | None = None):
        """
        Generate a magnet link from a torrent infohash.

        Args:
            trackers (list): Optional list of tracker URLs

        Returns:
            str: A complete magnet link
        """
        base = f"magnet:?xt=urn:btih:{self.hash}"

        if self.name:
            base += f"&dn={self.name.replace(' ', '+')}"  # Replace spaces for URL

        if trackers:
            for tracker in trackers:
                base += f"&tr={tracker}"

        return base
