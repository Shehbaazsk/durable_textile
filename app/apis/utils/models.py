from datetime import datetime
import uuid

from sqlalchemy import CHAR, BigInteger, Boolean, Column, DateTime, String
from app.config.database import Base


class CommonModel(Base):
    __abstract__ = True
    __allow_unmapped__ = True

    uuid = Column(CHAR(36),default=lambda : str(uuid.uuid4()),
                   unique=True, index=True, nullable=False)

    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime,
                         default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=False)
    is_delete = Column(Boolean, default=False)


class DocumentMaster(CommonModel):
    __tablename__ = "document_master"

    document_id = Column(BigInteger, primary_key=True, autoincrement=True)
    document_name = Column(String(255))
    file_path = Column(String(255)) # For SERVER with IP
    entity_type = Column(String(255))
    actual_path = Column(String(255)) #For LOCAL 
