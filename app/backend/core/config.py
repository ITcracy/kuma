import logging
import secrets
import sys
from typing import List

from databases import DatabaseURL
from loguru import logger
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret

from .logging import InterceptHandler

config = Config(".env")


class BaseConfig:
    API_PREFIX = "/api"
    JWT_TOKEN_PREFIX = "Token"  # noqa: S105
    VERSION = "0.0.0"
    DEBUG: bool = config("DEBUG", cast=bool, default=False)
    SECRET_KEY: Secret = config("SECRET_KEY", cast=Secret, default=secrets.token_urlsafe(128))
    PROJECT_NAME: str = config("Kuma", default="Pandas user interface")
    ALLOWED_HOSTS: List[str] = config("ALLOWED_HOSTS", cast=CommaSeparatedStrings, default="")
    DATABASE_URL: DatabaseURL = config("DATABASE_URL", cast=DatabaseURL)
    JWT_SUBJECT = "access"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # one week
    # logging configuration
    LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
    logging.basicConfig(handlers=[InterceptHandler(level=LOGGING_LEVEL)], level=LOGGING_LEVEL)
    logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])


app_config = BaseConfig()
