from enum import Enum

from pydantic import BaseModel, field_validator, Field
from torznab_indexes_api.schemas import merge_models
from torznab_indexes_api.schemas.torznab_schemas import  SearchSchema, BaseRequestSchema
from torznab_indexes_api.core.types import EnsureDateTime
from torznab_indexes_api.core.utils import parse_size

class FunctionType(str, Enum):
    caps = "caps"
    search = "search"


class AllParamsSchemas(merge_models(
    "AllParams",
    SearchSchema)):
    pass

class RarbgRequestSchema(BaseRequestSchema):

    search_params: SearchSchema | None = Field(default=None)

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
        return [
            item.strip() for item in value.split("/")
        ]

    @property
    def size_bytes(self) -> int:
        return parse_size(self.size)
