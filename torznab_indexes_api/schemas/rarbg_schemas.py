from enum import Enum
import PTN

from pydantic import BaseModel, field_validator, Field, computed_field
from torznab_indexes_api.schemas import merge_models
from torznab_indexes_api.schemas.torznab_schemas import  SearchSchema, BaseRequestSchema, TvSearchSchema, MovieSearchSchema, BaseTorrentItemSchema
from torznab_indexes_api.core.types import EnsureDateTime
from torznab_indexes_api.core.utils import parse_size

class FunctionType(str, Enum):
    caps = "caps"
    search = "search"
    tvsearch = "tvsearch"
    movie = "movie"


class RarbgSearchSchema(SearchSchema):
    MAX_EXTERNAL = 50
    MAX_INTERNAL = 20


class AllParamsSchemas(merge_models(
    "AllParams",
    RarbgSearchSchema, TvSearchSchema, MovieSearchSchema)):
    pass


class RarbgRequestSchema(BaseRequestSchema):

    search_params: TvSearchSchema | MovieSearchSchema | RarbgSearchSchema | None = Field(default=None, union_mode="left_to_right")

    def search_terms(self):
        return self.search_params.query



class RarbgItemSchema(BaseTorrentItemSchema):
    cat: str = Field(alias="cat")
    file: str
    release_name: str | None
    file_link: str
    magnet_link: str | None = None
    tags: list[str] = Field(default=[], alias="tags")
    language: str | None = None
    categories: list = Field(alias="category")
    added: EnsureDateTime
    size: str
    seeds: int = Field(alias="s")
    leechers: int = Field(alias="l")
    uploader: str

    @property
    def ptn_name(self) -> str:
        return self.release_name or self.file

    @field_validator("categories", mode="before")
    def categories_before(cls, value: str) -> list:
        return [ item.strip() for item in value.split("/") ]

    @property
    def size_bytes(self) -> int:
        return parse_size(self.size)
