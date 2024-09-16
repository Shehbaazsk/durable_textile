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
