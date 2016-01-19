from __future__ import with_statement
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import dictConfig

from blueberrypy.config import BlueberryPyConfiguration

# model's MetaData object
# for 'autogenerate' support
from GDGUkraine.model import metadata as target_metadata

environment = 'dev'

# If environment name was passed via command line argument
# e.g. -x environment=dev, let's use its value:
try:
    environment = [x.split('=')[1]
                   for x in context.config.cmd_opts.x
                   if x.split('=')[0] == 'environment'][0]
except:
    pass

conf = BlueberryPyConfiguration(environment=environment)
app_config = conf.app_config

sqlalchemy_config = conf.sqlalchemy_config

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

alembic_config = app_config.get('global', {}).get(config.config_ini_section)

# Update alembic's context. Just in case...
for option, value in alembic_config.items():
    if isinstance(value, str):
        config.set_main_option(option, value)
    else:
        config.attributes[option] = value
    config.set_section_option(
        config.config_ini_section, option, value)


# Interpret the config for Python logging.
# This line sets up loggers basically.
dictConfig(conf.logging_config)


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(target_metadata=target_metadata,
                      **sqlalchemy_config['sqlalchemy_engine'])

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        alembic_config,
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            user_module_prefix='GDGUkraine.model.',
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
