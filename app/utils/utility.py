
from functools import wraps
import os
import shutil
from fastapi import Depends, HTTPException, UploadFile,status
from werkzeug.utils import secure_filename
from app.apis.user.models import Role, User
from app.apis.utils.models import DocumentMaster
from app.config.database import get_session
from app.config.setting import get_settings
from app.config.logger_config import logger
from sqlalchemy.orm import Session
from app.config.security import decode_token, oauth2_scheme, verify_password

setting = get_settings()

def save_file(upload_file: UploadFile, folder_name: str, entity_type: str) -> int:
    """Save File to Server

    Args:
        upload_file (UploadFile): File to be uploaded
        folder_name (str): Folder name or Module name
        entity_type (str): It's Entity Type ex.images/jpg,

    Returns:
        int: document_id
    """

    try:
        logger.info(f"Attempting to save file: {upload_file.filename}, folder: {folder_name}, entity_type: {entity_type}")
        
        # Ensure the folder exists
        module_directory = os.path.join(setting.UPLOAD_FOLDER, folder_name)
        os.makedirs(module_directory, exist_ok=True)
        logger.info(f"Directory created or exists: {module_directory}")

        # Prepare file paths
        filename = secure_filename(upload_file.filename)
        file_path = os.path.join(module_directory, filename)
        logger.info(f"Saving file to: {file_path}")

        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        logger.info(f"File saved successfully: {filename}")

        # Create a document 
        document = DocumentMaster(
            document_name=filename,
            file_path=file_path,  
            entity_type=entity_type,
            actual_path=file_path  
        )

        with get_session() as session:
            session.add(document)
            session.commit()
            logger.info(f"Document saved to database with ID: {document.id}")
        
        return document.id

    except Exception as e:
        logger.error(f"Error saving file: {e}", exc_info=True)
        raise e


def authenticate_user(session: Session, email: str, password: str):
    user = session.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_current_user(token: str = Depends(oauth2_scheme)):
    token_data = decode_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data

# def role_required(allowed_roles: list):
    # def decorator(func):
    #     @wraps(func)
    #     async def wrapper(*args, db: Session = Depends(get_db), current_user: User = Depends(get_current_user), **kwargs):
    #         user_roles = [role.name for role in current_user.roles]
    #         if not any(role in allowed_roles for role in user_roles):
    #             raise HTTPException(
    #                 status_code=status.HTTP_403_FORBIDDEN,
    #                 detail="You do not have permission to access this resource"
    #             )
    #         return await func(*args, db=db, current_user=current_user, **kwargs)
    #     return wrapper
    # return decorator


# Dependency to get the current user (simulate authentication here)
# def get_current_user( user_id: int,db: Session = Depends(get_session)) -> User:
#     with get_session as session:
#         user = db.query(User).filter(User.id == user_id).first()
#     if user is None:
#         raise HTTPException(status_code=401, detail="User not found")
#     return user


# # Dependency to check if the user has a specific role
# def has_role(required_role: str):
#     def role_checker(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
#         # Fetch the role object from the database
#         role = db.query(Role).filter(Role.name == required_role).first()
#         if role not in current_user.roles:
#             raise HTTPException(status_code=403, detail="Not authorized")
#         return current_user
#     return role_checker