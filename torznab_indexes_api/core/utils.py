import re
from datetime import datetime
from dateutil.relativedelta import relativedelta


def parse_size(size: str) -> int:
    units = {"B": 1, "KB": 2**10, "MB": 2**20, "GB": 2**30, "TB": 2**40}
    unit = "".join(p for p in size if p.isalpha())
    number = size.replace(unit, "")
    return int(float(number)*units[unit.upper()])


def get_past_date(str_days_ago: str):

    def separate_number_from_words(value: str):
        match = re.match(r"([0-9]+)([^0-9_]+)", value, re.I)
        if match:
            return match.groups()
        return None

    now = datetime.now()
    split = " ".join(separate_number_from_words(str_days_ago)).split()
    if len(split) == 1 and split[0].lower() == "today":
        date = now.date()
    elif len(split) == 1 and split[0].lower() == "yesterday":
        date = now - relativedelta(days=1)
    elif split[1].lower() in ["mins", "min", "m"]:
        date = datetime.now() - relativedelta(minutes=int(split[0]))
    elif split[1].lower() in ["hour", "hours", "hr", "hrs", "h"]:
        date = datetime.now() - relativedelta(hours=int(split[0]))
    elif split[1].lower() in ["day", "days", "d"]:
        date = now - relativedelta(days=int(split[0]))
    elif split[1].lower() in ["wk", "wks", "week", "weeks", "w"]:
        date = now - relativedelta(weeks=int(split[0]))
    elif split[1].lower() in ["mon", "mons", "month", "months", "m"]:
        date = now - relativedelta(months=int(split[0]))
    elif split[1].lower() in ["yrs", "yr", "years", "year", "y"]:
        date = now - relativedelta(years=int(split[0]))
    else:
        raise ValueError("Wrong Argument format")

    return date

def to_kebab(value: str):
  return '-'.join(
    re.sub(r"(\s|_|-)+"," ",
    re.sub(r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+",
    lambda mo: ' ' + mo.group(0).lower(), value)).split())


CATEGORY_MAP = {
    # TV
    "TV": 5000,

    # Movies
    "MOVIES": 2000,
    "MOVIE": 2000,

    # Music
    "MUSIC": 3000,
    "MP3": 3010,
    "LOSSLESS": 3040,
    "FLAC": 3040,

    # Books
    "BOOKS": 7020,
    "E-BOOKS": 7020,
    "EBOOKS": 7020,

    # Adult
    "XXX": 6000,

    # Other
    "OTHER": 8000,
}

def get_category(tags: list[str]) -> int:
    # priority-based matching (first match wins)
    for tag in tags:
        tag_upper = tag.upper()
        if tag_upper in CATEGORY_MAP:
            return CATEGORY_MAP[tag_upper]

    return 8000  # fallback