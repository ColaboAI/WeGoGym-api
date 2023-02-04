import asyncio
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, inspect

from sqlalchemy.ext.asyncio import AsyncEngine

# import os, sys
from app.core import config as app_config
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# load_dotenv(os.path.join(BASE_DIR, ".env"))
# sys.path.append(BASE_DIR)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
import app.models as app_models

target_metadata = app_models.Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_database_uri():
    if app_config.settings.ENVIRONMENT == "DEV":
        return app_config.settings.LOCAL_SQLALCHEMY_DATABASE_URI
    else:
        return app_config.settings.DEFAULT_SQLALCHEMY_DATABASE_URI


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_database_uri()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    assert configuration
    configuration["sqlalchemy.url"] = get_database_uri()
    connectable = AsyncEngine(
        engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    # await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
# else:
#     run_migrations_online()
# else:
#     get_event_loop().run_until_complete(run_migrations_online())
else:
    asyncio.run(run_migrations_online())
