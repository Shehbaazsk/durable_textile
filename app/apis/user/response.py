from app.apis.user.schema import GenderEnum, RoleEnum
from app.apis.utils.response import BaseResponse


class RoleRespone(BaseResponse):
    name: str
    description: str


class UserDetailResponse(BaseResponse):
    first_name: str | None
    last_name: str | None
    email: str
    mobile_no: str | None
    gender: GenderEnum | None
    roles: list[RoleEnum] | None
    profile_image: str | None


class UserResponse(BaseResponse):
    first_name: str | None
    last_name: str | None
    email: str
    mobile_no: str | None
    gender: GenderEnum | None
    roles: list[RoleEnum] | None
    profile_image: str | None
