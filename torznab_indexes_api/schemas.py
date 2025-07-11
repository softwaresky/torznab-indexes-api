from typing import Iterable
from datetime import datetime
from dateutil import parser, tz

from enum import Enum, StrEnum

from pydantic import (
    BaseModel, model_validator, field_validator, Field, create_model
)
from pydantic_xml import BaseXmlModel, element, attr, xml_field_serializer
from pydantic_xml.element import XmlElementWriter

from fastapi import Query

from torznab_indexes_api.core.utils import parse_size, get_past_date

STANDARD_NAMESPACE_MAP = {
    "atom": "http://www.w3.org/2005/Atom",
    "torznab": "http://torznab.com/schemas/2015/feed"
}

class CategoryEnum(StrEnum):
    TV = "TV"
    MOVIES = "Movies"


# BaseModel
class SearchSchema(BaseModel):
    q: str | None = Field(default=None, description="Query string / search terms")
    cat: str | None = Field(default=None)
    attrs: list | None = Field(Query(default=None))
    offset: int | None = Field(default=None)
    limit: int | None = Field(default=None)

    @model_validator(mode="before")
    def _model_validator(cls, values: dict):
        diff = values.keys() - cls.model_fields.keys()
        if diff:
            raise ValueError(f"Invalid keys: {list(diff)}")

        return values

    @property
    def category(self) -> CategoryEnum | None:
        return None


class TvSearchSchema(SearchSchema):
    imdbid: str | None = Field(default=None)
    season: str | None = Field(default=None)
    ep: str | None = Field(default=None)

    @property
    def category(self) -> CategoryEnum | None:
        return CategoryEnum("TV")


class MovieSearchSchema(SearchSchema):
    imdbid: str | None = Field(default=None)
    genre: str | None = Field(default=None)

    @property
    def category(self) -> CategoryEnum | None:
        return CategoryEnum("Movie")


class FunctionType(Enum):
    caps = "caps"
    search = "search"
    tvsearch = "tvsearch"
    movie = "movie"


def merge_models(name: str, *models: Iterable[BaseModel]) -> BaseModel:
    fields = {}
    for model in models:
        f = {k: (v.annotation, v) for k, v in model.model_fields.items()}
        fields.update(f)
    return create_model(name, **fields)


class AllParamsSchemas(merge_models(
    "AllParams",
    SearchSchema, TvSearchSchema, MovieSearchSchema)):
    q: str | None = Field(default=None, description="Query string / search terms")


class TgxItemSchemaOld(BaseModel):
    type: str
    category: str = ""
    verified: str
    language: str = ""
    name: str
    torrent_url: str
    dl_url: str = Field(alias="dl")
    magnet: str = ""
    rating: str
    uploader: str
    size: int
    comments: int
    views: int
    seeders: int | None = None
    leechers: int | None = None
    added: datetime | None = None

    @field_validator("size", mode="before")
    def _parse_size(cls, v):
        if isinstance(v, str):
            return parse_size(v.replace(",", ""))
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

    @field_validator("comments", "views", mode="before")
    def parse_str_to_int(cls, v: str):
        return int(v.replace(",", ""))

    @model_validator(mode="before")
    def _model_validator(cls, values: dict):

        s_l = values.pop("s/l")
        # Seeders/Leechers
        if s_l and isinstance(s_l, str):
            s_l = s_l.replace("[", "").replace("]", "")
            seeders, leechers = s_l.split("/")
            values["seeders"] = int(cls.parse_str_to_int(seeders.strip()))
            values["leechers"] = int(cls.parse_str_to_int(leechers.strip()))

        return values


class TgxItemSchema(BaseModel):
    category: str = Field(default="", alias="c")
    verified: str = Field(default="", alias="checked by")
    language: str = ""
    name: str =  Field(alias="n")
    torrent_url: str = ""
    dl_url: str = Field(default="", alias="dl")
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



# BaseXMLModel
class TgxItemXmlSchema(BaseXmlModel, tag="item"):
    class Enclosure(BaseXmlModel):
        url: str = attr()
        type: str = attr(default="application/x-bittorrent")

    class StandardXmlItemSchema(BaseXmlModel):
        name: str = attr()
        value: str = attr()

    class IndexerXmlSchema(BaseXmlModel):
        id: str = attr()
        title: str

    title: str = element()
    guid: str = element()
    jackettindexer: IndexerXmlSchema = element()
    type: str = element()
    description: str = element()
    comments: str = element()
    pubDate: datetime = element()
    size: int = element()
    link: str = element()
    categories: list[str] = element(
        tag="category", default=[]
    )
    enclosure: Enclosure = element(default=None, nillable=True)
    attrs: list[StandardXmlItemSchema] = element(tag="attr", ns="torznab", default=[], nsmap={
        "torznab": "http://torznab.com/schemas/2015/feed"
    })

    @xml_field_serializer("pubDate")
    def _pub_date_serializer(
            self, element_: XmlElementWriter, value: datetime, field_name: str
    ):
        sub_element = element_.make_element(tag=field_name, nsmap=None)
        sub_element.set_text(value.strftime("%a, %d %b %Y %H:%M:%S %z"))
        element_.append_element(sub_element)

    @model_validator(mode="before")
    def _model_validator(cls, values: dict):
        return {
            "title": values["name"],
            "guid": values["magnet"],
            "type": "public",
            "jackettindexer": {
                "id": "TGx",
                "title": "Torrent Galaxy"
            },
            "comments": values["torrent_url"],
            "description": f"{values['name']} (leechers: {values['leechers']})",
            "size": values["size"],
            "pubDate": values["added"],
            "link": values["magnet"],
            "categories": [
                values["category"]
            ],
            "enclosure": {
                "url": values["magnet"],
                "type": "application/x-bittorrent"
            },
            "attrs": [
                {
                    "name": "category",
                    "value": values["category"],
                },
                {
                    "name": "seeders",
                    "value": str(values["seeders"]),
                },
                {
                    "name": "peers",
                    "value": str(values["seeders"]),
                },
                {
                    "name": "leechers",
                    "value": str(values["leechers"]),
                },
                {
                    "name": "magneturl",
                    "value": values["magnet"],
                },
                {
                    "name": "downloadvolumefactor",
                    "value": "0",
                },
                {
                    "name": "uploadvolumefactor",
                    "value": "1"
                },
                {
                    "name": "size",
                    "value": str(values["size"])
                }
            ]
        }


class TgxDataXmlSchema(BaseXmlModel, tag="channel"):
    class AtomXml(BaseXmlModel, ns="atom", tag="link"):
        href: str = attr()
        rel: str = attr(default="self")
        type: str = attr(default="application/atom+xml")

    atom_link: AtomXml = element(ns="atom", tag="link", default=None,
                                 nsmap={"atom": "http://www.w3.org/2005/Atom"})
    title: str = element(default="TGx")
    description: str = element(default="Torrent Galaxy site", nillable=True)
    link: str = element(default=None, nillable=True)
    language: str = element(default=None, nillable=True)
    category: str = element(default="search", nillable=True)
    items: list[TgxItemXmlSchema] = element(tag="item", default=[])


class RssResultSchema(BaseXmlModel, tag="rss", ns_attrs=True, nsmap=STANDARD_NAMESPACE_MAP):
    version: str = attr(default="2.0")
    channel: TgxDataXmlSchema = element()


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
