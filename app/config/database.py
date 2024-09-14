from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config.logger_config import logger
from app.config.setting import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URI,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=20,
    max_overflow=0,
    echo=settings.MYSQL_ECHO,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


Base = declarative_base()


def get_session() -> Generator:
    session = SessionLocal()
    try:
        yield session

    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        session.rollback()
        raise

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        session.rollback()
        raise

    finally:
        session.close()
