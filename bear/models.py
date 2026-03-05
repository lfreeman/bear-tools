from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, StrEnum


@dataclass
class Tag:
    title: str
    pk: int


@dataclass
class Note:
    title: str
    identifier: str
    creation_date: datetime
    modification_date: datetime
    tags: list[Tag] = field(default_factory=list)
    text: str = field(default_factory=str)


@dataclass
class Stats:
    total_notes: int
    trashed_notes: int
    total_tags: int
    orphaned_notes: int
    dups_notes: int


class SortBy(Enum):
    CREATED = "ZCREATIONDATE"
    MODIFIED = "ZMODIFICATIONDATE"


class Order(Enum):
    DESC = "desc"
    ASC = "asc"


class OutputFormat(StrEnum):
    TABLE = "table"
    JSON = "json"


class Period(StrEnum):
    WEEK = "week"
    DAY = "day"
