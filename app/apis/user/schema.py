from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class GenderEnum(str, Enum):
    MALE = 'M'
    FEMALE = 'F'


class UserCreateRequest(BaseModel):
    first_name: str | None = Field(..., examples=["John"])
    last_name: str | None = Field(..., examples=["Doe"])
    email: EmailStr = Field(..., examples=["john@example.com"])
    password: str = Field(..., min_length=8, max_length=100,
                          description="user password")
    mobile_no: str | None = Field(..., min_length=10, max_length=10, examples=[
                                  '1234567890'])
    gender: GenderEnum = Field(..., description="Gender must be 'M' or 'F'",
                               examples=["M", "F"])
