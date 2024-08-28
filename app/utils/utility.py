import os
import shutil
from datetime import datetime

import pytz
from fastapi import Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session
from werkzeug.utils import secure_filename

from app.config.database import get_session
from app.config.logger_config import logger
from app.config.security import get_current_user, verify_password
from app.config.setting import get_settings

setting = get_settings()


# Define the Indian timezone
INDIAN_TZ = pytz.timezone("Asia/Kolkata")


def get_current_indian_time() -> datetime:
    """Get the current time in Indian timezone."""
    return datetime.now(INDIAN_TZ)


def convert_to_indian_timezone(dt: datetime) -> datetime:
    """Convert a given datetime to Indian timezone."""
    if dt.tzinfo is None:
        # Localize naive datetime to Indian timezone
        return INDIAN_TZ.localize(dt)
    return dt.astimezone(INDIAN_TZ)


def save_file(
    upload_file: UploadFile, folder_name: str, entity_type: str, session: Session
) -> int:
    """Save File to Server

    Args:
        upload_file (UploadFile): File to be uploaded
        folder_name (str): Folder name or Module name
        entity_type (str): It's Entity Type ex.images/jpg,

    Returns:
        int: document_id
    """

    try:
        from app.apis.utils.models import DocumentMaster

        logger.info(f"Attempting to save file: {upload_file.filename}, folder: {
                    folder_name}, entity_type: {entity_type}")

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
            actual_path=file_path,
        )

        session.add(document)
        session.flush([document])
        logger.info(f"Document saved to database with ID: {
                    document.id}")

        return document.id

    except Exception as e:
        logger.error(f"Error saving file: {e}", exc_info=True)
        raise e


def authenticate_user(session: Session, email: str, password: str):
    from app.apis.user.models import User

    user = (
        session.query(User)
        .filter(User.email == email, User.is_active == True, User.is_delete == False)
        .first()
    )
    if not user:
        return False
    if not verify_password(password, user._password):
        return False
    return user


def has_role(required_role: str):
    from app.apis.user.models import Role, User

    def role_checker(
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
    ):
        role = db.query(Role).filter(Role.name == required_role).first()
        if role not in current_user.roles:
            raise HTTPException(status_code=404, detail="Role not found")
        return current_user

    return role_checker
