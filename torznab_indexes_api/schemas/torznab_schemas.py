from functools import cached_property
from enum import Enum, StrEnum
from typing import Any, ClassVar
from pydantic import BaseModel, field_validator, Field, ConfigDict, computed_field, model_validator
from pydantic_xml import BaseXmlModel, element, attr

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


class FunctionType(str, Enum):
    caps = "caps"
    search = "search"
    movie = "movie"


# BaseModel
class SearchSchema(BaseModel):
    MAX_INTERNAL: ClassVar[int] = 50
    MAX_EXTERNAL: ClassVar[int] = 50

    query: str = Field(default="top 10", description="Query string / search terms", alias="q")
    cat: str = Field(default="")
    attrs: list | None = Field(Query(default_factory=list))
    offset: int | None = Field(default=0, ge=0)
    limit: int | None = Field(default=50, gt=0)


    @model_validator(mode="after")
    def scale_values(self):
        ratio = self.MAX_EXTERNAL / self.MAX_INTERNAL

        if self.limit is not None:
            self.limit = max(1, int(self.limit * ratio))

        if self.offset is not None:
            self.offset = max(0, int(self.offset * ratio))

        return self

    @computed_field
    @property
    def page(self) -> int:
        if isinstance(self.offset, int) and isinstance(self.limit, int) and self.limit > 0:
            if self.offset > self.limit:
                return self.offset // self.limit
            else:
                return 1
        return 0


class ImdbSearchSchema(SearchSchema):
    imdbid: str | None = Field(default=None)

    @field_validator("imdbid", mode="before")
    @classmethod
    def imdbid_validator(cls, value: str) -> str:
        if not value.startswith("tt") and value.isdigit():
            return f"tt{value}"
        return value


class TvSearchSchema(ImdbSearchSchema):
    season: int | None = Field(default=None)
    episode: int | None = Field(default=None, alias="ep")


class MovieSearchSchema(ImdbSearchSchema):
    genre: str | None = Field(default=None)



class BaseRequestSchema(BaseModel):
    """Base Request structure"""

    search_params: TvSearchSchema | MovieSearchSchema | SearchSchema | None = Field(default=None, union_mode="left_to_right")

    def search_terms(self) -> Any:
        raise NotImplementedError()


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
    def ptn_name(self) -> str:
        raise NotImplementedError()

    @cached_property
    def ptn_data(self) -> TorrentTitleParseSchema:
        return TorrentTitleParseSchema.model_validate(PTN.parse(self.ptn_name))

    def ptn_validate(self, request_schema: BaseRequestSchema) -> bool:
        params = request_schema.search_params
        if isinstance(params, TvSearchSchema):
            if params.season:
                if params.season in self.ptn_data.season:
                    if params.episode:
                        if params.episode in self.ptn_data.episode:
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



