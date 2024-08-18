from fastapi import APIRouter, BackgroundTasks, Depends,  Form, status, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.orm import Session
from app.apis.user.response import UserDetailResponse, UserResponse
from app.apis.user.schema import (ChangePasswordRequest, ForgetPasswordRequest, GenderEnum,
                                  RefreshTokenRequest, ResetPasswordRequest, RoleEnum, UserFilters)
from app.apis.user.service import UserService
from app.config.database import get_session
from app.config.security import get_current_user
from app.utils.utility import has_role
from .models import User


user_router = APIRouter(prefix="/users", tags=['Users'])


@user_router.post('/signup', status_code=status.HTTP_201_CREATED, dependencies=[Depends(has_role('ADMIN'))])
def create_user(first_name: str = Form(..., examples=["John"]),
                last_name: str = Form(..., examples=["Doe"]),
                email: EmailStr = Form(..., examples=["john@example.com"]),
                password: str = Form(..., min_length=8, max_length=20,
                                     description="user password"),
                mobile_no: str | None = Form(min_length=10,
                                             max_length=10, examples=['1234567890']),
                gender: GenderEnum = Form(..., description="Gender must be 'M' or 'F'",
                                          examples=["M", "F"]),
                profile_image: UploadFile | None = None,
                role: RoleEnum = Form(..., description="role of the user"),
                session: Session = Depends(get_session)):
    """Create User endpoint

    Returns:
        tuple[dict,int]: A dict with msg and a status_code
    """

    return UserService.create_user(first_name, last_name, email, password, mobile_no, gender, profile_image, role, session)


@user_router.post('/login', status_code=status.HTTP_200_OK)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    """Login User Endpoint

    Returns:
        dict: A dict containing access_token,refresh_token and token type
    """

    return UserService.login_user(session, form_data)


@user_router.post('/refresh-token', status_code=status.HTTP_200_OK)
def refresh_token(refresh_token: RefreshTokenRequest, session: Session = Depends(get_session)):
    """Generate new token and refresh token endpoint

    Returns:
        dict: A dict containing access_token,refresh_token and token type
    """

    return UserService.refresh_token(refresh_token, session)


@user_router.put('/change-password', status_code=status.HTTP_202_ACCEPTED)
def change_password(data: ChangePasswordRequest, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """Change user password endpoint

    Returns:
        dict: A dict with message
    """

    return UserService.change_password(data, current_user, session)


@user_router.post('/forget-password', status_code=status.HTTP_200_OK)
async def forget_password(data: ForgetPasswordRequest, background_task: BackgroundTasks, session: Session = Depends(get_session)):
    """Forget user password endpoint

    Returns:
        dict: A dict with message
    """

    return await UserService.forget_password(data,  background_task, session)


@user_router.post('/reset-password', status_code=status.HTTP_200_OK)
def reset_password(token: str, data: ResetPasswordRequest, session: Session = Depends(get_session)):
    """Reset user password endpoiny

    Returns:
        dict: A dict with message
    """

    return UserService.reset_password(token, data, session)


@user_router.get("/me", response_model=UserDetailResponse, status_code=status.HTTP_200_OK)
def get_me(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """User detail endpoint

    Returns:
        dict: A dict with user information
    """

    return UserService.get_me(current_user, session)


@user_router.get("/", response_model=list[UserResponse], status_code=status.HTTP_200_OK, dependencies=[Depends(has_role('ADMIN'))])
def list_users(filters: UserFilters = Depends(), current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """List Users with filter endpoint

    Returns:
        dict: A list of dict with user information
    """
    return UserService.list_users(filters, current_user, session)
