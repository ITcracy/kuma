import pathlib
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))

from app.backend.core.config import app_config  # isort:skip
from app.backend.core.db import metadata  # isort:skip
from app.backend.user.models import user  # isort:skip

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = metadata

config.set_main_option("sqlalchemy.url", str(app_config.DATABASE_URL))


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        if app_config.DATABASE_URL.dialect == "sqlite":
            context.configure(
                connection=connection, target_metadata=target_metadata, render_as_batch=True
            )
        else:
            context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
