from enum import Enum

from pydantic import Field

from app.apis.utils.schema import BaseRequest


class CollectionSortEnum(Enum):
    name = "name"
    desc_name = "-name"
    created_at = "created_at"
    desc_created_at = "-created_at"


class CollectionFilters(BaseRequest):
    search_by: str | None = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=10, ge=1)
