from enum import Enum

from pydantic import Field

from app.apis.utils.schema import BaseRequest


class SampleCreateRequest(BaseRequest):
    name: str
    mill_reference_number: str | None
    construction: str | None
    composition: str | None
    gsm: int | None
    width: int | None
    count: str | None
    hanger_uuid: str | None


class SampleUpdateRequest(BaseRequest):
    name: str | None
    mill_reference_number: str | None
    construction: str | None
    composition: str | None
    gsm: int | None
    width: int | None
    count: str | None
    hanger_uuid: str | None


class SampleSortEnum(Enum):
    name = "name"
    desc_name = "-name"
    created_at = "created_at"
    desc_created_at = "-created_at"


class SampleFilters(BaseRequest):
    search_by: str | None = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=10, ge=1)
