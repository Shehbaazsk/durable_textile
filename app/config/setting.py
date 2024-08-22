from functools import lru_cache
import os
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # App
    APP_NAME:  str = os.environ.get("APP_NAME", "FastAPI")
    DEBUG: bool = bool(os.environ.get("DEBUG", False))

    # MySql Database Config
    MYSQL_HOST: str = os.environ.get("MYSQL_HOST", 'localhost')
    MYSQL_USER: str = os.environ.get("MYSQL_USER", 'root')
    MYSQL_PASS: str = os.environ.get("MYSQL_PASSWORD", 'root')
    MYSQL_PORT: int = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_DB: str = os.environ.get("MYSQL_DB", 'fastapi')
    MYSQL_ECHO: bool = os.environ.get("MYSQL_ECHO", True)
    DATABASE_URI: str = f"mysql+pymysql://{MYSQL_USER}:{
        MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

    # DOCUMENT_CONFIGURATION
    UPLOAD_FOLDER: str = os.environ.get("UPLOAD_FOLDER", "./uploads")

    # LOGGER_CONFIGURATION
    lOGGER_NAME: str = os.environ.get("LOGGER_NAME", 'fastapi')

    # JWT Secret Key
    JWT_SECRET: str = os.environ.get(
        "JWT_SECRET", "649fb93ef34e4fdf4187709c84d643dd61ce730d91856418fdcf563f895ea40f")
    JWT_ALGORITHM: str = os.environ.get("ACCESS_TOKEN_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 60*24*7))
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(
        os.environ.get("REFRESH_TOKEN_EXPIRE_MINUTES", 60*24*7))

    # App Secret Key
    APP_SECRET_KEY: str = os.environ.get(
        "APP_SECRET_KEY", "8deadce9449770680910741063cd0a3fe0acb62a8978661f421bbcbb66dc41f1")

    # EMAIL CONFIGURATION
    MAIL_USERNAME: str = os.environ.get("MAIL_USERNAME", "username")
    MAIL_PASSWORD: str = os.environ.get("MAIL_PASSWORD", "password")
    MAIL_FROM: str = os.environ.get("MAIL_FROM", "example@gmai.com")
    MAIL_PORT: int = os.environ.get("MAIL_PORT", 465)
    MAIL_SERVER: str = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_FROM_NAME: str = os.environ.get("MAIL_FROM_NAME", 'shehbaaz')
    MAIL_STARTTLS: str = os.environ.get("MAIL_STARTTLS", False)
    MAIL_SSL_TLS: str = os.environ.get("MAIL_SSL_TLS", True)

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
