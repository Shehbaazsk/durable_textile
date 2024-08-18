
from enum import Enum
from pydantic import BaseModel, ConfigDict


class BaseRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True,
                              validate_assignment=True,
                              use_enum_values=True,
                              str_strip_whitespace=True)


class SortOrderEnum(str, Enum):
    ASC = "asc"
    DESC = "desc"
