from fastapi import HTTPException, UploadFile, status
from sqlalchemy import exists, or_
from sqlalchemy.orm import Session

from app.apis.collection.models import Collection
from app.apis.hanger.models import Hanger
from app.apis.hanger.schema import HangerCreateRequest
from app.config.logger_config import logger
from app.utils.utility import save_file, set_id_if_exists_in_dict


class HangerService:
    @staticmethod
    def create_hanger(
        data: HangerCreateRequest, hanger_image: UploadFile | None, session=Session
    ):
        try:
            hanger_exists = session.query(
                exists().where(
                    or_(Hanger.name == data.name, Hanger.code == data.code),
                    Hanger.is_delete == False,
                )
            ).scalar()
            if hanger_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Hanger with name {data.name} or code {data.code} already exists",
                )

            hanger_data = data.model_dump()
            collection_uuid = hanger_data.pop("collection_uuid", None)

            if collection_uuid:
                if not set_id_if_exists_in_dict(
                    collection_uuid,
                    Collection,
                    Collection.id,
                    hanger_data,
                    "collection_id",
                    session,
                ):
                    return HTTPException(
                        status_code=404,
                        detail=f"Collection with uuid {hanger_data["collection_uuid"]} not found",
                    )

            hanger = Hanger(**hanger_data)
            session.add(hanger)
            session.flush()

            document_id = None
            if hanger_image:
                document_id = save_file(
                    hanger_image,
                    folder_name=f"hanger/{hanger.uuid}",
                    entity_type="HANGER-IMAGE",
                    session=session,
                )
            hanger.hanger_image_id = document_id
            session.add(hanger)
            session.commit()
            session.refresh(hanger, attribute_names=["uuid"])
            return {"message": "Hanger Created Sucessfully", "hanger_uuid": hanger.uuid}

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )
