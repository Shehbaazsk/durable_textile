from typing import Optional
from sqlalchemy import BigInteger, Column, Enum, ForeignKey, String
from sqlalchemy.orm import relationship
from app.apis.utils.models import CommonModel, DocumentMaster
from app.config.security import hash_password


class User(CommonModel):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100), unique=True, index=True, nullable=False)
    _password = Column(String(100))
    mobile_no = Column(String(10))
    gender = Column(Enum("M", "F"))
    profile_image_id = Column(BigInteger(),
                              ForeignKey('document_master.document_id'))
    profile_image = relationship("DocumentMaster",
                                 foreign_keys=[profile_image_id], backref="user_profile_image", uselist=False)

    @property
    def password(self):
        raise AttributeError("password: write-only field")

    @password.setter
    def password(self, password):
        self._password = hash_password(password)

    def __repr__(self):
        return f'<User {self.id}: {self.first_name} {self.last_name}>'


class Role(CommonModel):
    __tablename__ = 'roles'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True)
    description = Column(String(255))


class UserRole(CommonModel):
    __tablename__ = 'user_roles'

    user_id = Column(BigInteger, ForeignKey('users.id'), primary_key=True)
    role_id = Column(BigInteger, ForeignKey('roles.id'), primary_key=True)
