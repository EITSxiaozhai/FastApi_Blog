import os
from asyncio import current_task
from urllib import parse

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

# 从环境变量中获取值
db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_hostname = os.getenv("DB_HOSTNAME")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

db_password = parse.quote(db_password.encode('utf-8'))

Sql_URL = f"mysql+asyncmy://{db_username}:{db_password}@{db_hostname}:{db_port}/{db_name}?charset=utf8mb4"

# 创建异步连接
engine = create_async_engine(Sql_URL, pool_pre_ping=True, )

# 创建ORM模型操作方法
Base = declarative_base()

# 实例化异步操作
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=AsyncSession)

# 创建异步作用域会话
db_session = async_scoped_session(SessionLocal, scopefunc=current_task)

# # 这种方式适合需要精确控制事务的场景，例如复杂的业务逻辑或需要细粒度错误处理的操作：
# @asynccontextmanager
# async def get_db():
#     session = SessionLocal()
#     try:
#         # 注意在生成器里显式开启事务
#         await session.begin()
#         yield session
#     except Exception as e:
#         # 如果有错误，进行回滚
#         await session.rollback()
#         raise e
#     finally:
#         # 无论如何都要关闭 session
#         await session.close()

async def get_db():
    try:
        db = db_session()
        yield db
    finally:
       await db.close()