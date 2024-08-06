from fastapi import APIRouter, Depends, status,UploadFile
from sqlalchemy.orm import Session
from app.apis.user.schema import UserCreateRequest
from app.apis.user.service import UserService
from app.config.database import get_session


user_router = APIRouter(prefix="/users", tags=['Users'])



@user_router.post('/', status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreateRequest, profile_image:UploadFile=None,session: Session = Depends(get_session)):
    return UserService.create_user(data,profile_image,session)
