from typing import Iterable
from datetime import datetime
from dateutil import parser, tz
from functools import cached_property
from enum import Enum, StrEnum

from pydantic import (
    BaseModel, field_validator, Field, create_model, ConfigDict
)
from pydantic_xml import BaseXmlModel, element, attr
import PTN

from fastapi import Query

from torznab_indexes_api.core.utils import get_past_date


STANDARD_NAMESPACE_MAP = {
    "atom": "http://www.w3.org/2005/Atom",
    "torznab": "http://torznab.com/schemas/2015/feed"
}

class CategoryEnum(StrEnum):
    TV = "TV"
    MOVIES = "Movies"


class FunctionType(Enum):
    caps = "caps"
    search = "search"
    tvsearch = "tvsearch"
    movie = "movie"


# BaseModel
class SearchSchema(BaseModel):
    query: str = Field(default="", description="Query string / search terms", alias="q")
    cat: str = Field(default="")
    attrs: list | None = Field(Query(default=None))
    offset: int | None = Field(default=None)
    limit: int | None = Field(default=None)

    # @model_validator(mode="before")
    # def _model_validator(cls, values: dict):
    #     diff = values.keys() - cls.model_fields.keys()
    #     if diff:
    #         raise ValueError(f"Invalid keys: {list(diff)}")
    #
    #     return values


    @property
    def page(self) -> int:
        if self.offset and self.limit:
            return self.offset // self.limit
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




def merge_models(name: str, *models: Iterable[BaseModel]) -> BaseModel:
    fields = {}
    for model in models:
        f = {k: (v.annotation, v) for k, v in model.model_fields.items()}
        fields.update(f)
    return create_model(name, **fields)


class AllParamsSchemas(merge_models(
    "AllParams",
    SearchSchema, TvSearchSchema, MovieSearchSchema)):
    pass

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



class TgxItemSchema(BaseModel):
    primary_key: str = Field(default="", alias="pk")
    category: str = Field(default="", alias="c")
    verified: str = Field(default="", alias="checked by")
    language: str = ""
    name: str =  Field(alias="n")
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
            infohash (str): 40-character hex infohash
            name (str): Optional display name of the torrent
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


## Torrents Client Schemas

class BaseRequestSchema(BaseModel):
    search_params: TvSearchSchema | MovieSearchSchema | SearchSchema | None = Field(default=None, union_mode="left_to_right")

    def search_terms(self) -> str:
        raise NotImplementedError()


class TGxRequestSchema(BaseRequestSchema):

    """Torrent Galaxy Request structure
    """

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

