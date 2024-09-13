from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from app.apis.utils.models import CommonModel


class Collection(CommonModel):
    __tablename__ = "collections"

    name = Column(String(50), unique=True, nullable=False)
    collection_image_id = Column(BigInteger(), ForeignKey("document_master.id"))

    # relationships
    profile_image = relationship(
        "DocumentMaster",
        foreign_keys=[collection_image_id],
        backref="collection_image",
    )

    def __repr__(self):
        return f"<{self.__tablename__} - {self.id}>"
