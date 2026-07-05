from functools import cached_property
from enum import Enum, StrEnum
from typing import Any, ClassVar
from pydantic import BaseModel, field_validator, Field, ConfigDict, computed_field, model_validator
from pydantic_xml import BaseXmlModel, element, attr

from torznab_indexes_api.schemas import merge_models

import PTN

from fastapi import Query
from torznab_indexes_api.core.types import EnsureList

STANDARD_NAMESPACE_MAP = {
    "atom": "http://www.w3.org/2005/Atom",
    "torznab": "http://torznab.com/schemas/2015/feed"
}


class CategoryEnum(StrEnum):
    TV = "TV"
    MOVIES = "Movies"


class FunctionType(StrEnum):
    caps = "caps"
    search = "search"
    movie = "movie"
    tvsearch = "tvsearch"


# -----------------------------
# Base shared params (ALL queries)
# -----------------------------
class TorznabBaseParams(BaseModel):
    apikey: str | None = None
    query: str = Field(default="top 10", description="Query string / search terms", alias="q")
    cat: str = Field(default="")
    attrs: str | None = None
    offset: int | None = Field(default=0, ge=0)
    limit: int | None = Field(default=50, gt=0)
    tag: str | None = None


    @computed_field
    @property
    def page(self) -> int:
        if isinstance(self.offset, int) and isinstance(self.limit, int) and self.limit > 0:
            if self.offset > self.limit:
                return self.offset // self.limit
            else:
                return 1
        return 0


# -----------------------------
# Generic search
# t=search
# -----------------------------
class SearchParams(TorznabBaseParams):
    query: str | None = Field(default=None, alias="q")



class ImdbBaseParams(SearchParams):
    imdbid: str | None = Field(default=None)
    genre: str | None = Field(default=None)

    @field_validator("imdbid", mode="before")
    @classmethod
    def imdbid_validator(cls, value: str | None) -> str:
        if value and not value.startswith("tt") and value.isdigit():
            return f"tt{value}"
        return value


# -----------------------------
# TV search
# t=tvsearch
# -----------------------------
class TvSearchParams(ImdbBaseParams):
    season: int | None = Field(default=None)
    episode: int | None = Field(default=None, alias="ep")
    rid: int| None = None
    tvdbid: int | None = None
    tvmazeid: int | None = None


# -----------------------------
# Movie search
# t=movie-search
# -----------------------------
class MovieSearchParams(ImdbBaseParams):
    pass


# -----------------------------
# Audio search
# t=audio-search
# -----------------------------
class AudioSearchParams(SearchParams):
    artist: str | None = None
    album: str | None = None


# -----------------------------
# Book search
# t=book-search
# -----------------------------
class BookSearchParams(SearchParams):
    author: str | None = None
    title: str | None = None


class AllParamsSchemas(merge_models(
    "AllParams",
    SearchParams, TvSearchParams, MovieSearchParams, AudioSearchParams, BookSearchParams)):
    pass



class TorrentTitleParseSchema(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )

    title: str | None = None
    year: int | None = None
    season: EnsureList[int] = Field(default_factory=list)
    episode: EnsureList[int] = Field(default_factory=list)
    language: EnsureList[str] = Field(default_factory=list)
    resolution: str | None = None
    quality: str | None = None
    codec: str | None = None
    audio: str | None = None
    network: str | None = None
    encoder: str | None = None
    group: str | None = None


## Base Schema Torrent Item
class BaseTorrentItemSchema(BaseModel):


    @property
    def category_id(self) -> int:
        raise NotImplementedError()

    @property
    def ptn_name(self) -> str:
        raise NotImplementedError()

    @cached_property
    def ptn_data(self) -> TorrentTitleParseSchema:
        return TorrentTitleParseSchema.model_validate(PTN.parse(self.ptn_name))

    def ptn_validate(self, season: str | int | None = None, episode: str | int | None = None) -> bool:
        if season:
            if season in self.ptn_data.season:
                if episode:
                    if episode in self.ptn_data.episode:
                        return True
                    else:
                        return False
                return True
            else:
                return False
        return True

## XML Schema
class NewznabEnclosure(BaseXmlModel, tag="enclosure"):
    url: str = attr()
    type: str = attr(default="application/x-bittorrent")

class NewznabTorznabAttr(BaseXmlModel, tag="attr", ns="torznab", nsmap={"torznab": "http://torznab.com/schemas/2015/feed"}):
    name: str = attr()
    value: str = attr()

class NewznabGuid(BaseXmlModel, tag="guid"):
    isPermaLink: str = attr(default="true")
    title: str

class NewznabItem(BaseXmlModel, tag="item"):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    title: str = element()
    guid: NewznabGuid = element(tag="guid")
    link: str = element()
    comments: str | None = element(default=None)
    pubDate: str = element()
    category: str = element()
    description: str = element()
    enclosure: NewznabEnclosure = element(default=None, nillable=True)
    attrs: list[NewznabTorznabAttr] = element(tag="attr", ns="torznab",default=[])



class NewznabChannel(BaseXmlModel, tag="channel"):
    title: str = element()
    description: str = element()
    link: str = element()
    item: list[NewznabItem] = element()


class RssResult(BaseXmlModel, tag="rss", ns_attrs=True, nsmap=STANDARD_NAMESPACE_MAP):
    version: str = attr(default="2.0")
    channel: NewznabChannel = element()


class CategoryAttrXmlSchema(BaseXmlModel):
    id: str = attr()
    name: str = attr()


class RssCapabilitiesSchema(BaseXmlModel, tag="caps"):
    class Server(BaseXmlModel, tag="server"):
        title: str = attr()

    class Limits(BaseXmlModel, tag="limits"):
        default: str = attr()
        max: str = attr()

    class Categories(BaseXmlModel, tag="categories"):
        class CategoryXmlSchema(CategoryAttrXmlSchema):
            sub_cats: list[CategoryAttrXmlSchema] = element(tag="subcat", default=None)

        categories: list[CategoryXmlSchema] = element(tag="category", default=None)

    class Searching(BaseXmlModel, tag="searching"):
        class SearchAttrXmlSchema(BaseXmlModel):
            available: str = attr(default="no")
            supportedParams: str = attr(default="")

        search: SearchAttrXmlSchema = element(tag="search")
        tv_search: SearchAttrXmlSchema = element(tag="tv-search")
        movie_search: SearchAttrXmlSchema = element(tag="movie-search")
        audio_search: SearchAttrXmlSchema = element(tag="audio-search")
        book_search: SearchAttrXmlSchema = element(tag="book-search")

    server: Server = element()
    limits: Limits = element()
    searching: Searching = element()
    categories: Categories = element()



