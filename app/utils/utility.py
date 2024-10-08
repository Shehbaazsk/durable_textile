import os
import shutil
from datetime import datetime
from typing import Any

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

        logger.info(
            f"Attempting to save file: {upload_file.filename}, folder: {folder_name}, entity_type: {entity_type}"
        )

        # Ensure the folder exists
        module_directory = os.path.join(setting.UPLOAD_FOLDER, folder_name)
        if not os.path.exists(module_directory):
            os.makedirs(module_directory, exist_ok=True)
        logger.info(f"Directory created or exists: {module_directory}")

        # Prepare file paths
        filename = secure_filename(upload_file.filename)
        file_path = os.path.join(module_directory, filename)
        absolute_file_path = os.path.abspath(file_path)
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
            actual_path=absolute_file_path,
        )

        session.add(document)
        session.flush([document])
        logger.info(f"Document saved to database with ID: {document.id}")

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


def has_role(required_roles: list[str]):
    from app.apis.user.models import Role, User

    def role_checker(
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
    ):
        required_roles_from_db = (
            db.query(Role.name).filter(Role.name.in_(required_roles)).all()
        )
        required_role_names = {role.name for role in required_roles_from_db}
        for role in current_user.roles:
            if role.name in required_role_names:
                return current_user
        raise HTTPException(status_code=403, detail="Access forbidden: Role not found")

    return role_checker


def get_id_by_uuid(uuid, model, model_id_field, session):
    """A utility function that retrieves the id of a record based on its uuid from a given model"""
    try:
        # Query to fetch the id using the uuid
        id = (
            session.query(model_id_field)
            .filter(model.uuid == uuid, model.is_delete == False)
            .scalar()
        )

        # If the ID is not found, return an error message
        if not id:
            return {"error": f"{model.__name__} id not found"}, 400

        # Return the found ID
        return id

    except Exception as e:
        # Log the exception and return an error message
        logger.exception(e)
        return {"error": str(e)}, 500


def set_id_if_exists_in_dict(
    uuid: str,
    model: Any,
    model_id_field: Any,
    data_dict: dict,
    data_dict_field: str,
    session: Session,
):
    """Retrieve the ID from a UUID and update the provided dictionary with the result."""

    id_result = get_id_by_uuid(uuid, model, model_id_field, session)

    # Check if id is int, if it's not then it is error and return False
    if isinstance(id_result, int):
        data_dict[data_dict_field] = id_result
        return True
    else:
        error_message, status_code = id_result
        logger.error(f"Failed to retrieve ID: {error_message}")
        return False
