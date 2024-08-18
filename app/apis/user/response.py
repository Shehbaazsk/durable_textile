from app.apis.user.schema import GenderEnum, RoleEnum
from app.apis.utils.response import BaseResponse


class UserDetailResponse(BaseResponse):
    first_name: str
    last_name: str
    email: str
    mobile_no: str
    gender: GenderEnum
    roles: list[RoleEnum]
    profile_image: str
