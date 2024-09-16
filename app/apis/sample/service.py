from fastapi import HTTPException, UploadFile, status
from sqlalchemy import exists
from sqlalchemy.orm import Session

from app.apis.hanger.models import Hanger
from app.apis.sample.models import Sample
from app.apis.sample.schema import SampleCreateRequest
from app.config.logger_config import logger
from app.utils.utility import save_file, set_id_if_exists_in_dict


class SampleService:
    @staticmethod
    def create_sample(
        data: SampleCreateRequest, sample_image: UploadFile | None, session=Session
    ):
        try:
            sample_exists = session.query(
                exists().where(
                    Sample.name == data.name,
                    Sample.is_delete == False,
                )
            ).scalar()
            if sample_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Hanger with name {data.name} already exists",
                )

            sample_data = data.model_dump()
            hanger_uuid = sample_data.pop("hanger_uuid", None)

            if hanger_uuid:
                if not set_id_if_exists_in_dict(
                    hanger_uuid,
                    Hanger,
                    Hanger.id,
                    sample_data,
                    "hanger_id",
                    session,
                ):
                    return HTTPException(
                        status_code=404,
                        detail=f"Hanger with uuid {hanger_uuid} not found",
                    )

            sample = Sample(**sample_data)
            session.add(sample)
            session.flush()

            if sample_image:
                document_id = save_file(
                    sample_image,
                    folder_name=f"sample/{sample.uuid}",
                    entity_type="SAMPLE-IMAGE",
                    session=session,
                )
                sample.sample_image_id = document_id
            session.add(sample)
            session.commit()
            session.refresh(sample, attribute_names=["uuid"])
            return {"message": "Sample Created Sucessfully", "sample_uuid": sample.uuid}

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )
