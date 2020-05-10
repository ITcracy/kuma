from loguru import logger

from .db import database


async def connect_to_db():
    await database.connect()
    logger.info("Connection to database successful.")


async def close_db_connection():
    logger.info("Closing db connection..")
    await database.disconnect()
