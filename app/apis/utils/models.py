import uuid

from sqlalchemy import CHAR, BigInteger, Boolean, Column, DateTime, String

from app.config.database import Base
from app.utils.utility import get_current_indian_time


class CommonModel(Base):
    __abstract__ = True
    __allow_unmapped__ = True

    id = Column(BigInteger(), primary_key=True, autoincrement=True)
    uuid = Column(
        CHAR(50),
        default=lambda: str(uuid.uuid4()),
        unique=True,
        index=True,
        nullable=False,
    )

    created_at = Column(DateTime, default=get_current_indian_time)
    modified_at = Column(
        DateTime, default=get_current_indian_time, onupdate=get_current_indian_time
    )
    is_active = Column(Boolean, default=True)
    is_delete = Column(Boolean, default=False)


class DocumentMaster(CommonModel):
    __tablename__ = "document_master"

    document_name = Column(String(255))
    file_path = Column(String(255))  # For SERVER with IP
    entity_type = Column(String(255))
    actual_path = Column(String(255))  # For LOCAL
