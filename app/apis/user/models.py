from sqlalchemy import BigInteger, Column, Enum, ForeignKey, String, Table
from sqlalchemy.orm import relationship

from app.apis.utils.models import CommonModel
from app.config.database import Base
from app.config.security import hash_password


class User(CommonModel):
    __tablename__ = "users"

    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100), unique=True, index=True, nullable=False)
    _password = Column(String(100))
    mobile_no = Column(String(10))
    gender = Column(Enum("M", "F"))
    profile_image_id = Column(BigInteger(), ForeignKey("document_master.id"))

    # relationships
    profile_image = relationship(
        "DocumentMaster",
        foreign_keys=[profile_image_id],
        backref="user_profile_image",
        uselist=False,
    )
    roles = relationship("Role", secondary="user_roles", backref="users")

    @property
    def password(self):
        raise AttributeError("password: write-only field")

    @password.setter
    def password(self, password):
        self._password = hash_password(password)

    def __repr__(self):
        return f"<{self.__tablename__} - {self.id}>"


class Role(CommonModel):
    __tablename__ = "roles"

    name = Column(String(50), unique=True)
    description = Column(String(255))

    def __repr__(self):
        return f"<{self.__tablename__} - {self.name}>"


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", BigInteger(), ForeignKey("users.id"), primary_key=True),
    Column("role_id", BigInteger(), ForeignKey("roles.id"), primary_key=True),
)
