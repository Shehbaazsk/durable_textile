from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.apis.utils.models import CommonModel


class Hanger(CommonModel):
    __tablename__ = "hangers"

    name = Column(String(50), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    mill_reference_number = Column(String(255))
    construction = Column(String(255))
    composition = Column(String(255))
    gsm = Column(Integer())
    width = Column(Integer())
    count = Column(String(255))

    collection_id = Column(BigInteger(), ForeignKey("collections.id"))

    # relationships
    collection = relationship(
        "Collection",
        foreign_keys=[collection_id],
        backref="collection_hanger",
    )

    def __repr__(self):
        return f"<{self.__tablename__} - {self.id}>"
