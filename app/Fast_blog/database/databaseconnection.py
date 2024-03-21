import os
from urllib import parse
from asyncio import current_task

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

##创建异步连接
engine = create_async_engine(Sql_URL)

##创建ORM模型操作方法
Base = declarative_base()

##实例化异步操作
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=AsyncSession)
db_session = async_scoped_session(SessionLocal, scopefunc=current_task)

##创建metadata操作对象
