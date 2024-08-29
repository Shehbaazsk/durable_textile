from fastapi import HTTPException, UploadFile, status
from sqlalchemy import exists
from sqlalchemy.orm import Session

from app.apis.collection.models import Collection
from app.apis.utils.models import DocumentMaster
from app.config.logger_config import logger
from app.utils.utility import save_file


class CollectionService:
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

    def get_collection_by_uuid(
        collection_uuid: str,
        session: Session,
    ):
        try:
            collection = (
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
                .first()
            )
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
