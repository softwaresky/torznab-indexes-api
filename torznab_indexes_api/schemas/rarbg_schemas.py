from enum import Enum

from pydantic import BaseModel, field_validator, Field
from torznab_indexes_api.schemas import merge_models
from torznab_indexes_api.schemas.torznab_schemas import  SearchSchema, BaseRequestSchema
from torznab_indexes_api.core.types import EnsureDateTime
from torznab_indexes_api.core.utils import parse_size

class FunctionType(str, Enum):
    caps = "caps"
    search = "search"
    tvsearch = "tvsearch"
    movie = "movie"


class AllParamsSchemas(merge_models(
    "AllParams",
    SearchSchema)):
    pass


def scale_value(value: int) -> int:
    max_internal = 50  # Torznab default
    max_external = 20  # RarBg

    scaled = int(value * max_external / max_internal)
    return max(1, scaled)


class RarbgSearchSchema(SearchSchema):

    @field_validator("limit", "offset", mode="before")
    def validate_offset(cls, value: int) -> int:
        return scale_value(value)



class RarbgRequestSchema(BaseRequestSchema):

    search_params: RarbgSearchSchema | None = Field(default=None)

    def search_terms(self):
        return self.search_params.query



class RarbgItemSchema(BaseModel):
    cat: str = Field(alias="cat")
    file: str
    release_name: str | None
    file_link: str
    magnet_link: str | None = None
    tags: list[str] = Field(default=[], alias="tags")
    language: str | None = None
    size: int | None = None
    categories: list = Field(alias="category")
    added: EnsureDateTime
    size_bytes: int
    size: str
    seeds: int = Field(alias="s")
    leechers: int = Field(alias="l")
    uploader: str

    @field_validator("categories", mode="before")
    def categories_before(cls, value: str) -> list:
        return [ item.strip() for item in value.split("/") ]

    @property
    def size_bytes(self) -> int:
        return parse_size(self.size)
