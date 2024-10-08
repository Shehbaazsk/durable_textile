from datetime import timedelta

from fastapi import BackgroundTasks, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import asc, desc, exists, func
from sqlalchemy.orm import Query, Session

from app.apis.user.models import Role, User, user_roles
from app.apis.user.response import UserDetailResponse
from app.apis.user.schema import (
    ChangePasswordRequest,
    ForgetPasswordRequest,
    GenderEnum,
    RefreshTokenRequest,
    ResetPasswordRequest,
    RoleEnum,
    UserFilters,
    UserSortEnum,
    UserUpdateRequest,
)
from app.apis.utils.models import DocumentMaster
from app.config import setting
from app.config.logger_config import logger
from app.config.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.utils.email_utility import EmailRequest, send_email
from app.utils.utility import authenticate_user, save_file

settings = setting.get_settings()


class UserService:
    @staticmethod
    def create_user(
        first_name,
        last_name,
        email,
        password,
        mobile_no,
        gender,
        profile_image,
        role,
        session: Session,
    ):
        try:
            user_exists = session.query(
                exists().where(
                    User.email == email,
                    User.is_delete == False,
                )
            ).scalar()
            if user_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with email {email} already exists",
                )

            db_user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                mobile_no=mobile_no,
                gender=gender,
            )
            db_user.password = password

            db_role = session.query(Role).filter(Role.name == role).first()
            if not db_role:
                return {"error": f"Role with {role} not found"}, 404
            db_user.roles.append(db_role)
            session.add(db_user)
            session.flush(db_user)

            document_id = None
            if profile_image:
                document_id = save_file(
                    profile_image,
                    folder_name=f"users/profile_images/{db_user.uuid}/",
                    entity_type="PROFILE-IMAGE",
                    session=session,
                )
            db_user.profile_image_id = document_id
            session.add(db_user)
            session.commit()
            return {"message ": "User Created Successfully"}

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )

    @staticmethod
    def login_user(session: Session, data: OAuth2PasswordRequestForm):
        try:
            user = authenticate_user(session, data.username, data.password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            access_token_expires = timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
            access_token = create_access_token(
                data={"sub": user.email}, expires_delta=access_token_expires
            )

            refresh_token_expires = timedelta(
                minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
            )
            refresh_token = create_refresh_token(
                data={"sub": user.email}, expires_delta=refresh_token_expires
            )
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )

    @staticmethod
    def refresh_token(refresh_token: RefreshTokenRequest, session: Session):
        try:
            payload = decode_token(refresh_token.refresh_token)
            user_email = payload.get("email")
            if user_email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
                )

            access_token_expires = timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
            access_token = create_access_token(
                data={"sub": user_email}, expires_delta=access_token_expires
            )
            refresh_token_expires = timedelta(
                minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
            )
            refresh_token = create_refresh_token(
                data={"sub": user_email}, expires_delta=refresh_token_expires
            )

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )

    @staticmethod
    def change_password(
        data: ChangePasswordRequest, current_user: User, session: Session
    ):
        try:
            if not verify_password(data.old_password, current_user._password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password"
                )
            current_user.password = data.new_password
            session.add(current_user)
            session.commit()
            return JSONResponse({"message": "Password change successfully"})
        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )

    @staticmethod
    async def forget_password(
        data: ForgetPasswordRequest, background_task: BackgroundTasks, session: Session
    ):
        try:
            user = (
                session.query(User.email, User.first_name)
                .filter(
                    User.email == data.email,
                    User.is_delete == False,
                    User.is_active == True,
                )
                .first()
            )
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
                )
            token = create_access_token(
                data={"sub": user.email}, expires_delta=timedelta(minutes=5)
            )
            reset_link = f"http:localhost:8000/api/users/reset-password?token={
                token}"
            email_request_data = EmailRequest(
                subject="Forget Password",
                template_body={"name": user.first_name, "reset_link": reset_link},
                to_email=user.email,
                template_name="forgot_password_template.html",
                is_html=True,
            )

            background_task.add_task(send_email, email_request_data)

            return JSONResponse({"message": "Email with reset link sent successfully"})
        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )

    @staticmethod
    def reset_password(token: str, data: ResetPasswordRequest, session: Session):
        try:
            payload = decode_token(token)
            user_email = payload.get("email")
            if user_email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
                )
            user = (
                session.query(User)
                .filter(
                    User.email == user_email,
                    User.is_active == True,
                    User.is_delete == False,
                )
                .first()
            )
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            user.password = data.new_password
            session.add(user)
            session.commit()
            return JSONResponse({"message": "Password reset successfully"}, 200)

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )

    @staticmethod
    def get_me(current_user: User, session: Session):
        try:
            user = UserDetailResponse(
                uuid=current_user.uuid,
                first_name=current_user.first_name,
                last_name=current_user.last_name,
                email=current_user.email,
                mobile_no=current_user.mobile_no,
                gender=GenderEnum(current_user.gender),
                roles=[RoleEnum(role.name) for role in current_user.roles],
                profile_image=current_user.profile_image.file_path
                if current_user.profile_image_id
                else None,
            )

            return user
        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )

    @staticmethod
    def list_users(
        filters: UserFilters,
        sort_by: list[UserSortEnum],
        current_user,
        session: Session,
    ):
        try:
            query = (
                session.query(
                    User.uuid,
                    User.first_name,
                    User.last_name,
                    User.email,
                    User.mobile_no,
                    User.gender,
                    func.group_concat(Role.name).label("roles"),
                    DocumentMaster.file_path.label("profile_image"),
                )
                .filter(User.is_delete == False, User.id != current_user.id)
                .outerjoin(user_roles, user_roles.c.user_id == User.id)
                .outerjoin(Role, Role.id == user_roles.c.role_id)
                .outerjoin(DocumentMaster, DocumentMaster.id == User.profile_image_id)
                .group_by(User.id)
            )
            query = UserService.query_criteria(query, filters, sort_by)
            query = query.all()
            return [
                {
                    "uuid": result.uuid,
                    "first_name": result.first_name,
                    "last_name": result.last_name,
                    "email": result.email,
                    "mobile_no": result.mobile_no,
                    "gender": result.gender,
                    "roles": result.roles.split(",") if result.roles else [],
                    "profile_image": result.profile_image,
                }
                for result in query
            ]

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )

    @staticmethod
    def query_criteria(query: Query, filters: UserFilters, sort_by: list[UserSortEnum]):
        if filters.first_name:
            query = query.filter(User.first_name.ilike(f"%{filters.first_name}%"))
        if filters.gender:
            query = query.filter(User.gender == filters.gender)
        if filters.mobile_no:
            query = query.filter(User.mobile_no.like(f"%{filters.mobile_no}%"))

        if sort_by:
            for sort in sort_by:
                field_name = sort.value.lstrip("-")
                try:
                    field = getattr(User, field_name)
                except AttributeError:
                    raise ValueError(f"Invalid sort field: {field_name}")
                if sort.value.startswith("-"):
                    query = query.order_by(desc(field))
                else:
                    query = query.order_by(asc(field))

        offset = (filters.page - 1) * filters.per_page
        query = query.offset(offset).limit(filters.per_page)

        return query

    @staticmethod
    def get_user_by_uuid(user_uuid: str, session: Session):
        try:
            user = (
                session.query(
                    User.uuid,
                    User.first_name,
                    User.last_name,
                    User.email,
                    User.mobile_no,
                    User.gender,
                    func.group_concat(Role.name).label("roles"),
                    DocumentMaster.file_path.label("profile_image"),
                )
                .outerjoin(user_roles, user_roles.c.user_id == User.id)
                .outerjoin(Role, Role.id == user_roles.c.role_id)
                .outerjoin(DocumentMaster, DocumentMaster.id == User.profile_image_id)
                .filter(User.uuid == user_uuid, User.is_delete == False)
                .group_by(User.id)
                .first()
            )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            return {
                "uuid": user.uuid,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "mobile_no": user.mobile_no,
                "gender": user.gender,
                "roles": user.roles.split(",") if user.roles else [],
                "profile_image": user.profile_image,
            }
        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )

    @staticmethod
    def activate_or_deactivate_user(user_uuid: str, session: Session):
        try:
            user = (
                session.query(User)
                .filter(User.uuid == user_uuid, User.is_delete == False)
                .first()
            )
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            msg = "activated" if not user.is_active else "deactivated"
            user.is_active = not user.is_active
            session.commit()

            return {"message": f"User  {msg} successfully"}

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )

    @staticmethod
    def delete_user(user_uuid: str, session: Session):
        try:
            user = (
                session.query(User)
                .filter(User.uuid == user_uuid, User.is_delete == False)
                .first()
            )
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            user.is_delete = True
            session.commit()

            return {"message": "User Deleted Successfully"}
        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )

    @staticmethod
    def update_user(
        user_uuid: str,
        data: UserUpdateRequest,
        profile_image: UploadFile | None,
        session: Session,
    ):
        try:
            user = (
                session.query(User)
                .filter(User.uuid == user_uuid, User.is_delete == False)
                .first()
            )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is deactived, contact Admin",
                )

            for attr in UserUpdateRequest.__annotations__.keys():
                new_value = getattr(data, attr, None)
                current_value = getattr(user, attr, None)

                if (
                    hasattr(user, attr)
                    and new_value not in ("", None)
                    and new_value != current_value
                ):
                    setattr(user, attr, new_value)

            if profile_image:
                document_id = save_file(
                    profile_image,
                    folder_name="users/profile_images",
                    entity_type="PROFILE-IMAGE",
                    session=session,
                )
                user.profile_image_id = document_id

            session.commit()
            return {"message": "User updated successfully."}

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )
