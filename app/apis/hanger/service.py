from fastapi import HTTPException, UploadFile, status
from sqlalchemy import asc, desc, exists, or_
from sqlalchemy.orm import Query, Session

from app.apis.collection.models import Collection
from app.apis.hanger.models import Hanger
from app.apis.hanger.schema import (
    HangerCreateRequest,
    HangerFilters,
    HangerSortEnum,
    HangerUpdateRequest,
)
from app.apis.user.models import User
from app.apis.user.schema import RoleEnum
from app.apis.utils.models import DocumentMaster
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
                        detail=f"Collection with uuid {collection_uuid} not found",
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

    @staticmethod
    def update_hanger(
        hanger_uuid: str,
        data: HangerUpdateRequest,
        hanger_image: UploadFile | None,
        session: Session,
    ):
        try:
            hanger = (
                session.query(Hanger)
                .filter(Hanger.uuid, Hanger.is_delete == False)
                .first()
            )
            if not hanger:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Hanger with uuid {hanger_uuid} not found",
                )
            if not hanger.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Hanger is deactivated, activate it first",
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
                        detail=f"Collection with uuid {collection_uuid} not found",
                    )

            for attr, new_value in hanger_data.items():
                if (
                    new_value not in ("", None)
                    and getattr(hanger, attr, None) != new_value
                ):
                    setattr(hanger, attr, new_value)

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
            return {"message": "Hanger Updated Sucessfully", "hanger_uuid": hanger_uuid}

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )

    @staticmethod
    def list_hangers(
        filters: HangerFilters,
        sort_by: list[HangerSortEnum],
        current_user: User,
        session: Session,
    ):
        try:
            query = (
                session.query(
                    Hanger.uuid,
                    Hanger.name,
                    Hanger.code,
                    Hanger.mill_reference_number,
                    Hanger.construction,
                    Hanger.composition,
                    Hanger.gsm,
                    Hanger.width,
                    Hanger.count,
                    Collection.uuid.label("collection_uuid"),
                    Collection.name.label("collection_name"),
                    DocumentMaster.file_path.label("hanger_image"),
                )
                .filter(Hanger.is_delete == False)
                .outerjoin(
                    Collection,
                    (Collection.id == Hanger.collection_id)
                    & (Collection.is_delete == False),
                )
                .outerjoin(
                    DocumentMaster,
                    (DocumentMaster.id == Hanger.hanger_image_id)
                    & (DocumentMaster.is_delete == False),
                )
            )

            query = HangerService.query_criteria(query, current_user, filters, sort_by)

            hangers = query.all()
            return hangers

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
        filters: HangerFilters,
        sort_by: list[HangerSortEnum],
    ):
        is_admin = any(role.name == RoleEnum.ADMIN for role in current_user.roles)
        if not is_admin:
            query = query.filter(Hanger.is_active == True)

        if filters.search_by:
            query = query.filter(
                or_(
                    Hanger.name.ilike(f"%{filters.search_by}%"),
                    Hanger.code.ilike(f"%{filters.search_by}%"),
                )
            )

        if sort_by:
            for sort in sort_by:
                field_name = sort.value.lstrip("-")
                try:
                    field = getattr(Hanger, field_name)
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
    def get_hanger_by_uuid(hanger_uuid: str, current_user: User, session: Session):
        try:
            is_admin = any(role.name == RoleEnum.ADMIN for role in current_user.roles)
            query = (
                session.query(
                    Hanger.uuid,
                    Hanger.name,
                    Hanger.code,
                    Hanger.mill_reference_number,
                    Hanger.construction,
                    Hanger.composition,
                    Hanger.gsm,
                    Hanger.width,
                    Hanger.count,
                    Collection.uuid.label("collection_uuid"),
                    Collection.name.label("collection_name"),
                    DocumentMaster.file_path.label("hanger_image"),
                )
                .filter(Hanger.uuid == hanger_uuid, Hanger.is_delete == False)
                .outerjoin(
                    Collection,
                    (Collection.id == Hanger.collection_id)
                    & (Collection.is_delete == False),
                )
                .outerjoin(
                    DocumentMaster,
                    (DocumentMaster.id == Hanger.hanger_image_id)
                    & (DocumentMaster.is_delete == False),
                )
            )
            if not is_admin:
                query = query.filter(Hanger.is_active == True)
            hanger = query.first()
            if not hanger:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Hanger not found",
                )

            return hanger

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )
