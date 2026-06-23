from typing import  Annotated, TypeVar, Union
from datetime import datetime
from dateutil import parser
from pydantic import BeforeValidator

T = TypeVar("T")


def convert_to_datetime(value: str) -> datetime:
    return parser.parse(value)

EnsureDateTime = Annotated[datetime, convert_to_datetime]


def ensure_list(value):
    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]

EnsureList = Annotated[list[T], BeforeValidator(ensure_list)]