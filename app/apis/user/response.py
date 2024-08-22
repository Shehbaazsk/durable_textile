from app.apis.user.schema import GenderEnum, RoleEnum
from app.apis.utils.response import BaseResponse, DocumentMasterResponse


class RoleRespone(BaseResponse):
    name: str
    description: str


class UserDetailResponse(BaseResponse):
    first_name: str
    last_name: str
    email: str
    mobile_no: str
    gender: GenderEnum
    roles: list[RoleEnum]
    profile_image: str


class UserResponse(BaseResponse):
    first_name: str | None
    last_name: str | None
    email: str
    mobile_no: str | None
    gender: GenderEnum | None
    roles: list[str] | None
    profile_image: str | None
