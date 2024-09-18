from app.apis.utils.response import BaseResponse


class ListSampleRespose(BaseResponse):
    name: str
    mill_reference_number: str | None
    construction: str | None
    composition: str | None
    gsm: int | None
    width: int | None
    count: str | None
    hanger_uuid: str | None
    hanger_name: str | None
    sample_image: str | None
