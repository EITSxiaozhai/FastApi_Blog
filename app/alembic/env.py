from logging.config import fileConfig
from urllib import parse
import os

import sqlalchemy_utils
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
import sys
from os.path import abspath, dirname

sys.path.append(dirname(dirname(abspath(__file__))))
config = context.config

# 优先从环境变量注入 sqlalchemy.url，避免在镜像中硬编码
# 支持两种方式：
# 1) 直接提供 DATABASE_URL（推荐用于迁移，使用同步驱动）
# 2) 提供 DB_USERNAME/DB_PASSWORD/DB_HOSTNAME/DB_PORT/DB_NAME 组合（MySQL示例）
database_url = os.getenv("DATABASE_URL")
if not database_url:
    db_username = os.getenv("DB_USERNAME")
    db_password = os.getenv("DB_PASSWORD")
    db_hostname = os.getenv("DB_HOSTNAME")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    if all([db_username, db_password, db_hostname, db_port, db_name]):
        # Alembic 迁移应使用同步驱动，这里使用已安装的 mysqlclient (mysqldb)
        safe_password = parse.quote(db_password.encode('utf-8'))
        database_url = (
            f"mysql+mysqldb://{db_username}:{safe_password}@{db_hostname}:{db_port}/{db_name}?charset=utf8mb4"
        )

if database_url:
    config.set_main_option("sqlalchemy.url", database_url)


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from Fast_blog.model.models import Base
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()




def render_item(type_, obj, autogen_context):
    """
    Apply custom rendering for selected items.
    """
    if type_ == 'type' and isinstance(obj, sqlalchemy_utils.types.choice.ChoiceType):
        # add import for this type
        autogen_context.imports.add("import sqlalchemy_utils")
        return "sqlalchemy_utils.types.choice.ChoiceType(choices=" + str(obj.choices) + ")"

    # default rendering for other objects
    return False



def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_item=render_item
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
