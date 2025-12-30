from typing import  Annotated
from datetime import datetime
from dateutil import parser, tz


def convert_to_datetime(value: str) -> datetime:
    return parser.parse(value)

EnsureDateTime = Annotated[datetime, convert_to_datetime]