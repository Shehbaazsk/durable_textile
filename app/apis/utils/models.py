from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, String
from app.config.database import Base


class CommonModel(Base):
    __abstract__ = True
    __allow_unmapped__ = True

    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime,
                         default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=False)
    is_delete = Column(Boolean, default=False)


class DocumentMaster(CommonModel):
    __tablename__ = "document_master"

    document_id = Column(BigInteger, primary_key=True, autoincrement=True)
    document_name = Column(String(255))
    file_path = Column(String(255))
    entity_type = Column(String(255))
    actual_path = Column(String(255))
