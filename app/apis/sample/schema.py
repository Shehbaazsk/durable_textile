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
