import logging
import os
import secrets
import sys
from typing import List, Union

from databases import DatabaseURL
from loguru import logger
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret

from app.core.logging import InterceptHandler

config = Config(".env")


class BaseConfig:
    API_PREFIX = "/api"
    JWT_TOKEN_PREFIX = "Token"  # noqa: S105
    VERSION = "0.0.0"
    DEBUG: bool = config("DEBUG", cast=bool, default=False)
    SECRET_KEY: Secret = config("SECRET_KEY", cast=Secret, default=secrets.token_urlsafe(128))
    PROJECT_NAME: str = config("Kuma", default="Pandas user interface")
    ALLOWED_HOSTS: List[str] = config(
        "ALLOWED_HOSTS", cast=CommaSeparatedStrings, default=""
    )
    # logging configuration
    LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
    logging.basicConfig(
        handlers=[InterceptHandler(level=LOGGING_LEVEL)], level=LOGGING_LEVEL
    )
    logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])


class DevConfig(BaseConfig):
    DEBUG = True
    DATABASE_URL: DatabaseURL = config("DEV_DB_CONNECTION", cast=DatabaseURL)


class ProdConfig(BaseConfig):
    DEBUG = False
    DATABASE_URl: DatabaseURL = config("PROD_DB_CONNECTION", cast=DatabaseURL)


def get_config() -> Union[DevConfig, ProdConfig]:
    environment = os.getenv("KUMA_ENV", "dev")
    if environment == "dev":
        return DevConfig()
    else:
        return ProdConfig()


app_config = get_config()
