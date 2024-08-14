from datetime import timedelta
import os
from fastapi import HTTPException, UploadFile,status
from fastapi.background import P
from app.apis.user.models import User
from app.apis.user.schema import UserCreateRequest, UserLoginRequest
from app.config import setting
from sqlalchemy.orm import Session
from app.apis.utils.models import DocumentMaster
from werkzeug.utils import secure_filename

from app.config.security import create_access_token, create_refresh_token
from app.utils.utility import authenticate_user, save_file

settings = setting.get_settings()


class UserService:

    def create_user(session: Session, data: UserCreateRequest, profile_image: UploadFile | None = None):
        document_id = None
        if profile_image:
            document_id = save_file(profile_image, module_name="users", entity_type="PROFILE-IMAGE")
        
        db_user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            mobile_no=data.mobile_no,
            gender=data.gender,
            profile_image_id=document_id
        )
        db_user.password = data.password

        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return {"message ":"User Created Successfully"}

    def login_user(session:Session,data:UserLoginRequest):
        try:
            user = authenticate_user(session,data.email,data.password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
            
            refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
            refresh_token = create_refresh_token(data={"sub": user.email}, expires_delta=refresh_token_expires)
            return {"access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer"},200
        except Exception as e:
            return {"error":str(e)},500