from databases import Database
from sqlalchemy import MetaData

from .config import app_config

database = Database(app_config.DATABASE_URL)
metadata = MetaData()
