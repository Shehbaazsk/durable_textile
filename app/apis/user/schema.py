from enum import Enum

from pydantic import EmailStr, Field

from app.apis.utils.schema import BaseRequest


class GenderEnum(str, Enum):
    MALE = "M"
    FEMALE = "F"


class RoleEnum(str, Enum):
    ADMIN = "ADMIN"
    STAFF = "STAFF"


class UserCreateRequest(BaseRequest):
    first_name: str | None = Field(..., examples=["John"])
    last_name: str | None = Field(examples=["Doe"])
    email: EmailStr = Field(..., examples=["john@example.com"])
    password: str = Field(..., min_length=8, max_length=20, description="user password")
    mobile_no: str | None = Field(min_length=10, max_length=10, examples=["1234567890"])
    gender: GenderEnum = Field(
        ..., description="Gender must be 'M' or 'F'", examples=["M", "F"]
    )
    role: RoleEnum = Field(..., description="Role of user")


class UserUpdateRequest(BaseRequest):
    first_name: str | None = Field(None, examples=["John"])
    last_name: str | None = Field(None, examples=["Doe"])
    mobile_no: str | None = Field(
        None, min_length=10, max_length=10, examples=["1234567890"]
    )
    gender: GenderEnum | None = Field(
        None, description="Gender must be 'M' or 'F'", examples=["M", "F"]
    )


class UserLoginRequest(BaseRequest):
    email: str
    password: str


class Token(BaseRequest):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseRequest):
    email: EmailStr | None = None


class RefreshTokenRequest(BaseRequest):
    refresh_token: str


class ChangePasswordRequest(BaseRequest):
    old_password: str
    new_password: str


class ForgetPasswordRequest(BaseRequest):
    email: EmailStr


class ResetPasswordRequest(BaseRequest):
    new_password: str


class UserSortEnum(Enum):
    gender = "gender"
    created_at = "created_at"
    desc_created_at = "-created_at"


class UserFilters(BaseRequest):
    first_name: str | None = None
    gender: GenderEnum | None = None
    mobile_no: str | None = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=10, ge=1)
