import os
from fastapi import UploadFile
from app.apis.user.models import User
from app.apis.user.schema import UserCreateRequest
from app.config.database import get_session
from sqlalchemy.orm import Session
from app.apis.utils.models import DocumentMaster


class UserService:

    @staticmethod
    def save_profile_image(file: UploadFile, user_id: int):
        file_location = f"uploads/profile_images/{user_id}/{file.filename}"
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        with open(file_location, "wb") as f:
            f.write(file.file.read())
        document_master = DocumentMaster(
            document_name=file.filename,
            file_path=file_location,
            entity_type="USER-PROFILE",
            actual_path=file_location
        )
        return document_master
    
    def create_user(data: UserCreateRequest,profile_image:UploadFile|None, session: Session):

        if session.query(User).filter(User.email==data.email,User.is_delete==False).count() > 0:
            raise ValueError("User with this email already exists")
        user = User(
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
            mobile_no=data.mobile_no,
            gender=data.gender.value
        )
        user.password = data.password
        if profile_image:
            document_master = save
        session.add(user)
        session.commit()
        return user
