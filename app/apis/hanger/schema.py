from app.apis.utils.schema import BaseRequest


class HangerCreateRequest(BaseRequest):
    name: str
    code: str
    mill_reference_number: str | None
    construction: str | None
    composition: str | None
    gsm: str | None
    width: str | None
    count: str | None
    collection_uuid: str | None
