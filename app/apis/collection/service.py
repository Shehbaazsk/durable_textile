from fastapi import HTTPException, UploadFile, status
from sqlalchemy import asc, desc, exists
from sqlalchemy.orm import Query, Session

from app.apis.collection.models import Collection
from app.apis.collection.schema import CollectionFilters, CollectionSortEnum
from app.apis.user.models import User
from app.apis.user.schema import RoleEnum
from app.apis.utils.models import DocumentMaster
from app.config.logger_config import logger
from app.utils.utility import save_file


class CollectionService:
    @staticmethod
    def create_collection(
        name: str,
        collection_image: UploadFile | None,
        session: Session,
    ):
        try:
            collection_exist = session.query(
                exists().where(
                    Collection.name == name,
                    Collection.is_delete == False,
                )
            ).scalar()
            if collection_exist:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Collection with name {name} already exists",
                )

            collection = Collection(name=name)
            session.add(collection)
            session.flush()

            document_id = None
            if collection_image:
                document_id = save_file(
                    collection_image,
                    folder_name=f"collections/{collection.id}",
                    entity_type="COLLECTION-IMAGE",
                    session=session,
                )
                collection.collection_image_id = document_id
            session.commit()
            session.refresh(collection, attribute_names=["uuid"])
            return {
                "message": "Collection Created Successfully",
                "collection_uuid": collection.uuid,
            }

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )

    @staticmethod
    def update_collection(
        collection_uuid: str,
        name: str | None,
        collection_image: UploadFile | None,
        session: Session,
    ):
        try:
            collection = (
                session.query(Collection.id, Collection.name)
                .filter(
                    Collection.uuid == collection_uuid, Collection.is_delete == False
                )
                .first()
            )
            if not collection:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Collection not found",
                )
            if name and name != "" and name != collection.name:
                collection.name = name

            document_id = None
            if collection_image:
                document_id = save_file(
                    collection_image,
                    folder_name=f"collections/{collection.id}",
                    entity_type="COLLECTION-IMAGE",
                    session=session,
                )
                collection.collection_image_id = document_id
            session.commit()
            return {
                "message": "Collection Updated Successfully",
                "collection_uuid": collection_uuid,
            }

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )

    @staticmethod
    def get_collection_by_uuid(
        collection_uuid: str,
        current_user: User,
        session: Session,
    ):
        try:
            is_admin = any(role.name == RoleEnum.ADMIN for role in current_user.roles)
            query = (
                session.query(
                    Collection.uuid,
                    Collection.name,
                    DocumentMaster.file_path.label("collection_image"),
                )
                .filter(
                    Collection.uuid == collection_uuid, Collection.is_delete == False
                )
                .outerjoin(
                    DocumentMaster,
                    (DocumentMaster.id == Collection.collection_image_id)
                    & (DocumentMaster.is_delete == False),
                )
            )

            if not is_admin:
                query = query.filter(Collection.is_active == True)

            collection = query.first()
            if not collection:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Collection not found",
                )

            return collection

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )

    @staticmethod
    def list_collections(
        filters: CollectionFilters,
        sort_by: list[CollectionSortEnum],
        current_user: User,
        session: Session,
    ):
        try:
            query = (
                session.query(
                    Collection.uuid,
                    Collection.name,
                    DocumentMaster.file_path.label("collection_image"),
                )
                .filter(Collection.is_delete == False)
                .outerjoin(
                    DocumentMaster,
                    (DocumentMaster.id == Collection.collection_image_id)
                    & (DocumentMaster.is_delete == False),
                )
            )

            query = CollectionService.query_criteria(
                query, current_user, filters, sort_by
            )
            collections = query.all()
            return collections

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
        filters: CollectionFilters,
        sort_by: list[CollectionSortEnum],
    ):
        is_admin = any(role.name == RoleEnum.ADMIN for role in current_user.roles)
        if not is_admin:
            query = query.filter(Collection.is_active == True)

        if filters.search_by:
            query = query.filter(Collection.name.ilike(f"%{filters.search_by}%"))

        if sort_by:
            for sort in sort_by:
                field_name = sort.value.lstrip("-")
                try:
                    field = getattr(Collection, field_name)
                except AttributeError:
                    raise ValueError(f"Invalid sort field: {field_name}")
                if sort.value.startswith("-"):
                    query = query.order_by(desc(field))
                else:
                    query = query.order_by(asc(field))

        offset = (filters.page - 1) * filters.per_page
        query = query.offset(offset).limit(filters.per_page)

        return query
