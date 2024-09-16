from enum import Enum

from pydantic import Field

from app.apis.utils.schema import BaseRequest


class HangerCreateRequest(BaseRequest):
    name: str
    code: str
    mill_reference_number: str | None
    construction: str | None
    composition: str | None
    gsm: int | None
    width: int | None
    count: str | None
    collection_uuid: str | None


class HangerUpdateRequest(BaseRequest):
    name: str | None
    code: str | None
    mill_reference_number: str | None
    construction: str | None
    composition: str | None
    gsm: int | None
    width: int | None
    count: str | None
    collection_uuid: str | None


class HangerSortEnum(Enum):
    name = "name"
    desc_name = "-name"
    created_at = "created_at"
    desc_created_at = "-created_at"


class HangerFilters(BaseRequest):
    search_by: str | None = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=10, ge=1)
