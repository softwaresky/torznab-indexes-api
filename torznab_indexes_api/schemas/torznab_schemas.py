from enum import Enum, StrEnum
from typing import Any
from pydantic import (
    BaseModel, field_validator, Field, ConfigDict, computed_field
)
from pydantic_xml import BaseXmlModel, element, attr

from fastapi import Query


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
    query: str = Field(default="top 10", description="Query string / search terms", alias="q")
    cat: str = Field(default="")
    attrs: list | None = Field(Query(default=None))
    offset: int | None = Field(default=0, ge=0)
    limit: int | None = Field(default=50, gt=0)

    # @model_validator(mode="before")
    # def _model_validator(cls, values: dict):
    #     diff = values.keys() - cls.model_fields.keys()
    #     if diff:
    #         raise ValueError(f"Invalid keys: {list(diff)}")
    #
    #     return values

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
    imdbid: str | None = None

    @field_validator("imdbid", mode="before")
    @classmethod
    def imdbid_validator(cls, value: str) -> str:
        if not value.startswith("tt") and value.isdigit():
            return f"tt{value}"
        return value


class TvSearchSchema(ImdbSearchSchema):
    season: int | None = None
    episode: int | None = Field(default=None, alias="ep")


class MovieSearchSchema(ImdbSearchSchema):
    genre: str | None = None



class BaseRequestSchema(BaseModel):
    """Base Request structure
    """

    search_params: TvSearchSchema | MovieSearchSchema | SearchSchema | None = Field(
        default=None, union_mode="left_to_right"
    )

    def search_terms(self) -> Any:
        raise NotImplementedError()


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

    # class IndexerXmlSchema(BaseXmlModel):
    #     id: str = attr()
    #     title: str

    title: str = element()
    guid: NewznabGuid = element(tag="guid")
    link: str = element()
    comments: str | None = element(default=None)
    pubDate: str = element()
    # categories: list[str] = element(
    #     tag="category", default=[]
    # )
    category: str = element()
    description: str = element()
    # jackettindexer: IndexerXmlSchema = element()
    # type: str = element()
    enclosure: NewznabEnclosure = element(default=None, nillable=True)
    attrs: list[NewznabTorznabAttr] = element(tag="attr", ns="torznab",default=[])



class NewznabChannel(BaseXmlModel, tag="channel"):
    title: str = element()
    description: str = element()
    link: str = element()
    item: list[NewznabItem] = element()


# class TgxDataXmlSchema(BaseXmlModel, tag="channel"):
#     class AtomXml(BaseXmlModel, ns="atom", tag="link"):
#         href: str = attr()
#         rel: str = attr(default="self")
#         type: str = attr(default="application/atom+xml")
#
#     atom_link: AtomXml = element(ns="atom", tag="link", default=None,
#                                  nsmap={"atom": "http://www.w3.org/2005/Atom"})
#     title: str = element(default="TGx")
#     description: str = element(default="Torrent Galaxy site", nillable=True)
#     link: str = element(default=None, nillable=True)
#     language: str = element(default=None, nillable=True)
#     category: str = element(default="search", nillable=True)
#     items: list[NewznabItemSchema] = element(tag="item", default=[])


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



