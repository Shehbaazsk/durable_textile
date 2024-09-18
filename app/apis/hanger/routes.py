from fastapi import APIRouter, Depends, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.apis.hanger.response import ListHangerRespose
from app.apis.hanger.schema import (
    HangerCreateRequest,
    HangerFilters,
    HangerSortEnum,
    HangerUpdateRequest,
)
from app.apis.hanger.service import HangerService
from app.apis.user.models import User
from app.apis.user.schema import RoleEnum
from app.config.database import get_session
from app.config.security import get_current_user
from app.utils.utility import has_role

hanger_router = APIRouter(prefix="/hangers", tags=["Hangers"])


@hanger_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_role([RoleEnum.ADMIN]))],
)
def create_hanger(
    name: str = Form(...),
    code: str = Form(...),
    mill_reference_number: str | None = Form(default=None),
    construction: str | None = Form(default=None),
    composition: str | None = Form(default=None),
    gsm: int | None = Form(default=None),
    width: int | None = Form(default=None),
    count: str | None = Form(default=None),
    collection_uuid: str | None = Form(default=None),
    hanger_image: UploadFile | None = None,
    session: Session = Depends(get_session),
):
    """Create a new hanger endpoint

    Returns:
        tuple[dict,int]: A dict with msg and a status_code
    """

    data = HangerCreateRequest(
        name=name,
        code=code,
        mill_reference_number=mill_reference_number,
        construction=construction,
        composition=composition,
        gsm=gsm,
        width=width,
        count=count,
        collection_uuid=collection_uuid,
    )

    return HangerService.create_hanger(data, hanger_image, session)


@hanger_router.patch(
    "/hanger_uuid",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(has_role([RoleEnum.ADMIN]))],
)
def update_hanger(
    hanger_uuid: str,
    name: str | None = Form(default=None),
    code: str | None = Form(default=None),
    mill_reference_number: str | None = Form(default=None),
    construction: str | None = Form(default=None),
    composition: str | None = Form(default=None),
    gsm: int | None = Form(default=None),
    width: int | None = Form(default=None),
    count: str | None = Form(default=None),
    collection_uuid: str | None = Form(default=None),
    hanger_image: UploadFile | None = None,
    session: Session = Depends(get_session),
):
    """Update hanger endpoint

    Returns:
        tuple[dict,int]: A dict with msg and a status_code
    """

    data = HangerUpdateRequest(
        name=name,
        code=code,
        mill_reference_number=mill_reference_number,
        construction=construction,
        composition=composition,
        gsm=gsm,
        width=width,
        count=count,
        collection_uuid=collection_uuid,
    )

    return HangerService.update_hanger(hanger_uuid, data, hanger_image, session)


@hanger_router.get(
    "/hanger_uuid",
    status_code=status.HTTP_200_OK,
    response_model=ListHangerRespose,
)
def get_hanger_by_uuid(
    hanger_uuid: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get hanger by UUID endpoint

    Returns:
        tuple[dict,int]: A dict with hanger data and a status_code
    """

    return HangerService.get_hanger_by_uuid(hanger_uuid, current_user, session)


@hanger_router.get(
    "/", status_code=status.HTTP_200_OK, response_model=list[ListHangerRespose]
)
def list_hangers(
    filters: HangerFilters = Depends(),
    sort_by: list[HangerSortEnum] = Query(default=HangerSortEnum.desc_created_at),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List hangers endpoint

    Returns:
        tuple[dict,int]: A dict with hanger data and a status_code
    """
    filters = filters
    sort_by = sort_by
    current_user = current_user
    session = session

    return HangerService.list_hangers(filters, sort_by, current_user, session)


@hanger_router.get(
    "/hanger_uuid/change-status",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(has_role([RoleEnum.ADMIN]))],
)
def change_hanger_status(
    hanger_uuid: str,
    session: Session = Depends(get_session),
):
    """Change hanger status endpoint

    Returns:
        tuple[dict,int]: A dict with change status message and a status_code
    """

    return HangerService.change_hanger_status(hanger_uuid, session)


@hanger_router.delete(
    "/hanger_uuid",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(has_role([RoleEnum.ADMIN]))],
)
def delete_hanger(
    hanger_uuid: str,
    session: Session = Depends(get_session),
):
    """Change hanger status endpoint

    Returns:
        tuple[dict,int]: A dict with delete message and a status_code
    """

    return HangerService.delete_hanger(hanger_uuid, session)
