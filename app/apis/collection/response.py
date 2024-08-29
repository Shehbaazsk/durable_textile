from app.apis.utils.response import BaseResponse


class GetCollectionRespose(BaseResponse):
    name: str
    collection_image: str | None
