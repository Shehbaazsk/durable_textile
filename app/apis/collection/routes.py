from fastapi import APIRouter, Depends, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.apis.collection.response import GetCollectionRespose
from app.apis.collection.schema import CollectionFilters, CollectionSortEnum
from app.apis.collection.service import CollectionService
from app.apis.user.models import User
from app.config.database import get_session
from app.config.security import get_current_user
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
    """Create a new collection endpoint

    Returns:
        tuple[dict,int]: A dict with msg and a status_code
    """

    return CollectionService.create_collection(name, collection_image, session)


@collection_router.patch(
    "/collection_uuid",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(has_role("ADMIN"))],
)
def update_collection(
    collection_uuid: str,
    name: str | None = Form(None),
    collection_image: UploadFile | None = None,
    session: Session = Depends(get_session),
):
    """Update a collection endpoint

    Returns:
        tuple[dict,int]: A dict with msg and a status_code
    """

    return CollectionService.update_collection(
        collection_uuid, name, collection_image, session
    )


@collection_router.get(
    "/collection_uuid",
    status_code=status.HTTP_200_OK,
    response_model=GetCollectionRespose,
)
def get_collection_by_uuid(
    collection_uuid: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get collection by UUID endpoint

    Returns:
        tuple[dict,int]: A dict with collection data and a status_code
    """

    return CollectionService.get_collection_by_uuid(
        collection_uuid, current_user, session
    )


@collection_router.get(
    "/", status_code=status.HTTP_200_OK, response_model=list[GetCollectionRespose]
)
def list_collections(
    filters: CollectionFilters = Depends(),
    sort_by: list[CollectionSortEnum] = Query(
        default=CollectionSortEnum.desc_created_at
    ),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List collections endpoint

    Returns:
        tuple[dict,int]: A dict with collections data and a status_code
    """

    return CollectionService.list_collections(filters, sort_by, current_user, session)
