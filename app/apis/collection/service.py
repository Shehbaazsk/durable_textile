from fastapi import HTTPException, UploadFile, status
from sqlalchemy import exists
from sqlalchemy.orm import Session

from app.apis.collection.models import Collection
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

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later.",
            )
