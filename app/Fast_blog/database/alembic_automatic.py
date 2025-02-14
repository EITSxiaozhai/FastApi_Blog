import os
from alembic.config import Config
from alembic import command

from Fast_blog.database.databaseconnection import Sql_URL


def ConfigGeneration():
    try:
        print("数据库文件检查")
        # 创建 Alembic 配置实例
        alembic_cfg = Config()
        # 基础设定根据实际情况调整
        alembic_cfg.set_main_option("script_location", "./")
        alembic_cfg.set_main_option("sqlalchemy.url", Sql_URL)
        print("数据库文件开始迁移")
        # 执行迁移
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        print(e)