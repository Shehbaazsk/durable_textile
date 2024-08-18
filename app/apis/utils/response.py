
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class BaseResponse(BaseModel):
    uuid: UUID
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True,
                              validate_assignment=True,
                              use_enum_values=True,
                              str_strip_whitespace=True)


class DocumentMasterResponse(BaseResponse):
    document_name: str
    file_path: str
    entity_type: str
