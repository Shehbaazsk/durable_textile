from datetime import timedelta
from fastapi import HTTPException, UploadFile,status
from fastapi.security import OAuth2PasswordRequestForm
from app.apis.user.models import Role, User
from app.apis.user.schema import UserCreateRequest, UserLoginRequest
from app.config import setting
from sqlalchemy.orm import Session


from app.config.security import create_access_token, create_refresh_token
from app.utils.utility import authenticate_user, save_file

settings = setting.get_settings()


class UserService:

    def create_user(first_name, last_name, email, password, mobile_no, gender, profile_image, role,session:Session):
        document_id = None
        if profile_image:
            document_id = save_file(profile_image, folder_name="users/profile_images", entity_type="PROFILE-IMAGE",session=session)
        
        db_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile_no=mobile_no,
            gender=gender,
            profile_image_id=document_id
        )
        db_user.password = password

        db_role = session.query(Role).filter(Role.name==role).first()
        if not db_role:
            return {"error":f"Role with {role} not found"},404
        db_user.roles.append(db_role)
        session.add(db_user)
        session.commit()
        return {"message ":"User Created Successfully"}

    def login_user(session:Session,data:OAuth2PasswordRequestForm):
        try:
            user = authenticate_user(session,data.username,data.password)
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
                    "token_type": "bearer"}
        except Exception as e:
            return {"error":str(e)},500