from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.apis.utils.models import CommonModel


class Sample(CommonModel):
    __tablename__ = "sample"

    name = Column(String(255), nullable=False, unique=True)
    mill_reference_number = Column(String(255))
    buyer_reference_construction = Column(String(255))
    composition = Column(String(255))
    construction = Column(String(255))
    gsm = Column(Integer())
    width = Column(Integer())
    count = Column(String(255))

    hanger_id = Column(BigInteger(), ForeignKey("hangers.id"))
    sample_image_id = Column(BigInteger(), ForeignKey("document_master.id"))

    # relationships
    hanger = relationship(
        "Hanger",
        foreign_keys=[hanger_id],
        backref="hanger_sample",
    )
    sample_image = relationship(
        "DocumentMaster",
        foreign_keys=[sample_image_id],
        backref="sample_image",
    )
