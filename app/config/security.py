from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.apis.user.schema import TokenData
from app.config.database import get_session
from app.config.setting import get_settings
from passlib.context import CryptContext
import pytz

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenScheme(BaseModel):
    email: Optional[str] = EmailStr


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    from app.utils.utility import get_current_indian_time
    to_encode = data.copy()
    expire = get_current_indian_time() + (expires_delta if expires_delta else timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    from app.utils.utility import get_current_indian_time
    to_encode = data.copy()
    expire = get_current_indian_time() + (expires_delta if expires_delta else timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET,
                             algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise jwt.PyJWTError
        return TokenData(email=email).model_dump()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


def get_current_user(db: Session = Depends(get_session), token: str = Depends(oauth2_scheme)):
    from app.apis.user.models import User
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
        token_data = TokenScheme(email=email)
    except Exception:
        raise credentials_exception
    user = db.query(User).filter(User.email == token_data.email,
                                 User.is_delete == False, User.is_active == True).first()
    if user is None:
        raise credentials_exception
    return user
