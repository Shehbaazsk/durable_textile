from fastapi import APIRouter, UploadFile, status
from fastapi.params import Depends, Form
from sqlalchemy.orm import Session

from app.apis.sample.schema import SampleCreateRequest, SampleUpdateRequest
from app.apis.sample.service import SampleService
from app.apis.user.schema import RoleEnum
from app.config.database import get_session
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
    "/",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(has_role([RoleEnum.ADMIN]))],
)
def update_sample(
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
