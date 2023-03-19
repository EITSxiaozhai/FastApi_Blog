from asyncio import current_task
from typing import AsyncGenerator

from urllib import  parse
import  sys
from asyncio import current_task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


sys.path.append('../')

password = parse.quote("@XU15964352xu")
##使用utf8进行中文输入
Sql_URL = "mysql+asyncmy://django:"+ password + "@mysql.exploit-db.xyz/Fastapi_blog" + "?charset=utf8mb4"
engine = create_async_engine(Sql_URL)

Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=AsyncSession)
db_session = async_scoped_session(SessionLocal, scopefunc=current_task)