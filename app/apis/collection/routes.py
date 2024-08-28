from fastapi import APIRouter, Depends, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.apis.collection.service import CollectionService
from app.config.database import get_session
from app.utils.utility import has_role

collection_router = APIRouter(prefix="/collections", tags=["Collections"])


@collection_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_role("ADMIN"))],
)
def create_collection(
    name: str = Form(...),
    collection_image: UploadFile | None = None,
    session: Session = Depends(get_session),
):
    """Create a new collection

    Returns:
        tuple[dict,int]: A dict with msg and a status_code
    """

    return CollectionService.create_collection(name, collection_image, session)
