# ----- coding: utf-8 ------
# author: YAO XU time:
import uuid
from sqlalchemy import select
from app.Fast_blog import model
from app.Fast_blog.database.database import engine
from sqlalchemy.orm import sessionmaker
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from  fastapi import APIRouter
from app.Fast_blog.database.database import db_session
from app.Fast_blog.model import models

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
Session = SessionLocal()


UserApp = APIRouter()

templates = Jinja2Templates(directory="./Fast_blog/templates")

UserApp.mount("/static", StaticFiles(directory="./Fast_blog/static"), name="static")


def UUID_crt(UuidApi):
    x = uuid.uuid5(uuid.NAMESPACE_DNS,UuidApi)
    return x

@UserApp.get("/")
async def query():
    async with db_session() as session:
        sql = select(models.user).where(models.user.gender == 1)
        print(sql) # 这里可以打印出sql
        result = await session.execute(sql)
        # 第一条数据
        data = result.scalars().first()
        # 所有数据
        # data = result.scalars().all()
    return ("查询成功")