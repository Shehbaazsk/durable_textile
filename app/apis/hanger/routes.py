from fastapi import APIRouter, Depends, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.apis.hanger.schema import HangerCreateRequest
from app.apis.hanger.service import HangerService
from app.apis.user.schema import RoleEnum
from app.config.database import get_session
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
