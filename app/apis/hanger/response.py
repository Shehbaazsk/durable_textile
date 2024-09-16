from app.apis.utils.response import BaseResponse


class ListHangerRespose(BaseResponse):
    name: str
    code: str
    mill_reference_number: str | None
    construction: str | None
    composition: str | None
    gsm: int | None
    width: int | None
    count: str | None
    collection_uuid: str | None
    collection_name: str | None
    hanger_image: str | None
