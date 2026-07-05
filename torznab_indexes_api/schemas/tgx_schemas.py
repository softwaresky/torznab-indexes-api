from datetime import datetime
from enum import Enum

from dateutil import parser, tz

from pydantic import field_validator, Field
from torznab_indexes_api.core.utils import get_past_date, get_category
from torznab_indexes_api.schemas.torznab_schemas import BaseTorrentItemSchema


class FunctionType(str, Enum):
    caps = "caps"
    search = "search"
    tvsearch = "tvsearch"
    movie = "movie"


class TgxItemSchema(BaseTorrentItemSchema):
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

    @property
    def ptn_name(self) -> str:
        return self.name

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

    @property
    def category_id(self) -> int:
        return get_category([self.category])