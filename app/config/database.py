from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

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
    finally:
        session.close()
