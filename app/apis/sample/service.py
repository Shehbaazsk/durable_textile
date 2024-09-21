from fastapi import HTTPException, UploadFile, status
from sqlalchemy import asc, desc, exists
from sqlalchemy.orm import Query, Session

from app.apis.hanger.models import Hanger
from app.apis.sample.models import Sample
from app.apis.sample.schema import (
    SampleCreateRequest,
    SampleFilters,
    SampleSortEnum,
    SampleUpdateRequest,
)
from app.apis.user.models import User
from app.apis.user.schema import RoleEnum
from app.apis.utils.models import DocumentMaster
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

    @staticmethod
    def update_sample(
        sample_uuid: str,
        data: SampleUpdateRequest,
        sample_image: UploadFile | None,
        session: Session,
    ):
        try:
            sample = (
                session.query(Sample)
                .filter(Sample.uuid, Sample.is_delete == False)
                .first()
            )
            if not sample:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Sample with uuid {sample_uuid} not found",
                )
            if not sample.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Sample is deactivated, activate it first",
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

            for attr, new_value in sample_data.items():
                if (
                    new_value not in ("", None)
                    and getattr(sample, attr, None) != new_value
                ):
                    setattr(sample, attr, new_value)

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
            return {"message": "Sample Updated Sucessfully", "sample_uuid": sample_uuid}

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )

    @staticmethod
    def get_sample_by_uuid(sample_uuid: str, current_user: User, session: Session):
        try:
            is_admin = any(role.name == RoleEnum.ADMIN for role in current_user.roles)
            query = (
                session.query(
                    Sample.uuid,
                    Sample.name,
                    Sample.mill_reference_number,
                    Sample.construction,
                    Sample.composition,
                    Sample.gsm,
                    Sample.width,
                    Sample.count,
                    Hanger.uuid.label("hanger_uuid"),
                    Hanger.name.label("hanger_name"),
                    DocumentMaster.file_path.label("sample_image"),
                )
                .filter(Sample.uuid == sample_uuid, Sample.is_delete == False)
                .outerjoin(
                    Hanger,
                    (Hanger.id == Sample.hanger_id) & (Hanger.is_delete == False),
                )
                .outerjoin(
                    DocumentMaster,
                    (DocumentMaster.id == Sample.sample_image_id)
                    & (DocumentMaster.is_delete == False),
                )
            )
            if not is_admin:
                query = query.filter(Sample.is_active == True)
            sample = query.first()
            if not sample:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sample not found",
                )

            return sample

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )

    staticmethod

    def list_samples(
        filters: SampleFilters,
        sort_by: list[SampleSortEnum],
        current_user: User,
        session: Session,
    ):
        try:
            query = (
                session.query(
                    Sample.uuid,
                    Sample.name,
                    Sample.mill_reference_number,
                    Sample.construction,
                    Sample.composition,
                    Sample.gsm,
                    Sample.width,
                    Sample.count,
                    Hanger.uuid.label("hanger_uuid"),
                    Hanger.name.label("hanger_name"),
                    DocumentMaster.file_path.label("sample_image"),
                )
                .filter(Sample.is_delete == False)
                .outerjoin(
                    Hanger,
                    (Hanger.id == Sample.hanger_id) & (Hanger.is_delete == False),
                )
                .outerjoin(
                    DocumentMaster,
                    (DocumentMaster.id == Sample.sample_image_id)
                    & (DocumentMaster.is_delete == False),
                )
            )

            query = SampleService.query_criteria(query, current_user, filters, sort_by)

            samples = query.all()
            return samples

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )

    @staticmethod
    def query_criteria(
        query: Query,
        current_user: User,
        filters: SampleFilters,
        sort_by: list[SampleSortEnum],
    ):
        is_admin = any(role.name == RoleEnum.ADMIN for role in current_user.roles)
        if not is_admin:
            query = query.filter(Sample.is_active == True)

        if filters.search_by:
            query = query.filter(Sample.name.ilike(f"%{filters.search_by}%"))

        if sort_by:
            for sort in sort_by:
                field_name = sort.value.lstrip("-")
                try:
                    field = getattr(Sample, field_name)
                except AttributeError:
                    raise ValueError(f"Invalid sort field: {field_name}")
                if sort.value.startswith("-"):
                    query = query.order_by(desc(field))
                else:
                    query = query.order_by(asc(field))

        offset = (filters.page - 1) * filters.per_page
        query = query.offset(offset).limit(filters.per_page)

        return query

    @staticmethod
    def change_sample_status(sample_uuid: str, session: Session):
        try:
            sample = (
                session.query(Sample)
                .filter(Sample.uuid == sample_uuid, Sample.is_delete == False)
                .first()
            )
            if not sample:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="sample not found"
                )
            msg = "activated" if not sample.is_active else "deactivated"
            sample.is_active = not sample.is_active
            session.commit()

            return {"message": f"sample {msg} successfully", "sample_uuid": sample_uuid}

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )

    @staticmethod
    def delete_sample(sample_uuid: str, session: Session):
        try:
            sample = (
                session.query(Sample)
                .filter(Sample.uuid == sample_uuid, Sample.is_delete == False)
                .first()
            )
            if not sample:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="sample not found"
                )
            sample.is_delete = True
            session.commit()

            return {"message": "sample deleted successfully"}

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )
