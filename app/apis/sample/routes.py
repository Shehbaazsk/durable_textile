from fastapi import APIRouter, Query, UploadFile, status
from fastapi.params import Depends, Form
from sqlalchemy.orm import Session

from app.apis.sample.response import ListSampleRespose
from app.apis.sample.schema import (
    SampleCreateRequest,
    SampleFilters,
    SampleSortEnum,
    SampleUpdateRequest,
)
from app.apis.sample.service import SampleService
from app.apis.user.models import User
from app.apis.user.schema import RoleEnum
from app.config.database import get_session
from app.config.security import get_current_user
from app.utils.utility import has_role

sample_router = APIRouter(prefix="/sample", tags=["Samples"])


@sample_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_role([RoleEnum.ADMIN]))],
)
def create_sample(
    name: str = Form(...),
    mill_reference_number: str | None = Form(default=None),
    construction: str | None = Form(default=None),
    composition: str | None = Form(default=None),
    gsm: int | None = Form(default=None),
    width: int | None = Form(default=None),
    count: str | None = Form(default=None),
    hanger_uuid: str | None = Form(default=None),
    sample_image: UploadFile | None = None,
    session: Session = Depends(get_session),
):
    """Create a new sample endpoint

    Returns:
        tuple[dict,int]: A dict with msg and a status_code
    """

    data = SampleCreateRequest(
        name=name,
        mill_reference_number=mill_reference_number,
        construction=construction,
        composition=composition,
        gsm=gsm,
        width=width,
        count=count,
        hanger_uuid=hanger_uuid,
    )

    return SampleService.create_sample(data, sample_image, session)


@sample_router.patch(
    "/sample_uuid",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(has_role([RoleEnum.ADMIN]))],
)
def update_sample(
    sample_uuid: str,
    name: str = Form(default=None),
    mill_reference_number: str | None = Form(default=None),
    construction: str | None = Form(default=None),
    composition: str | None = Form(default=None),
    gsm: int | None = Form(default=None),
    width: int | None = Form(default=None),
    count: str | None = Form(default=None),
    hanger_uuid: str | None = Form(default=None),
    sample_image: UploadFile | None = None,
    session: Session = Depends(get_session),
):
    """Create a new sample endpoint

    Returns:
        tuple[dict,int]: A dict with msg and a status_code
    """

    data = SampleUpdateRequest(
        name=name,
        mill_reference_number=mill_reference_number,
        construction=construction,
        composition=composition,
        gsm=gsm,
        width=width,
        count=count,
        hanger_uuid=hanger_uuid,
    )

    return SampleService.update_sample(data, sample_image, session)


@sample_router.get(
    "/sample_uuid",
    status_code=status.HTTP_200_OK,
    response_model=ListSampleRespose,
)
def get_sample_by_uuid(
    sample_uuid: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get sample by UUID endpoint

    Returns:
        tuple[dict,int]: A dict with sample data and a status_code
    """

    return SampleService.get_sample_by_uuid(sample_uuid, current_user, session)


@sample_router.get(
    "/", status_code=status.HTTP_200_OK, response_model=list[ListSampleRespose]
)
def list_sample(
    filters: SampleFilters = Depends(),
    sort_by: list[SampleSortEnum] = Query(default=SampleSortEnum.desc_created_at),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List sample endpoint

    Returns:
        tuple[dict,int]: A dict with sample data and a status_code
    """

    return SampleService.list_samples(filters, sort_by, current_user, session)


# # @sample_router.get(
# #     "/hanger_uuid/change-status",
# #     status_code=status.HTTP_200_OK,
# #     dependencies=[Depends(has_role([RoleEnum.ADMIN]))],
# # )
# # def change_hanger_status(
# #     hanger_uuid: str,
# #     session: Session = Depends(get_session),
# # ):
# #     """Change hanger status endpoint

# #     Returns:
# #         tuple[dict,int]: A dict with change status message and a status_code
# #     """

# #     return HangerService.change_hanger_status(hanger_uuid, session)


# # @sample_router.delete(
# #     "/hanger_uuid",
# #     status_code=status.HTTP_200_OK,
# #     dependencies=[Depends(has_role([RoleEnum.ADMIN]))],
# # )
# # def delete_hanger(
# #     hanger_uuid: str,
# #     session: Session = Depends(get_session),
# # ):
# #     """Change hanger status endpoint

# #     Returns:
# #         tuple[dict,int]: A dict with delete message and a status_code
# #     """

# #     return HangerService.delete_hanger(hanger_uuid, session)
