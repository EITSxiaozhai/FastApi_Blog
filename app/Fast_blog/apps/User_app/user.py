# ----- coding: utf-8 ------
# author: YAO XU time:
import asyncio
import uuid
from cgitb import text

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy_utils import EmailType

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


async def UUID_crt(UuidApi):
    UuidGenerator = uuid.uuid5(uuid.NAMESPACE_DNS,UuidApi)
    return UuidGenerator

@UserApp.get("/")
async def query(inputname:str,inpassword:str,inEmail:EmailStr,ingender:bool):
    async with db_session() as session:
            try:
                if session.get(models.User.username, inputname):
                    x = models.User(username=inputname,userpassword=inpassword,UserEmail=inEmail,gender=ingender,UserUuid=str((UUID_crt(inputname))))
                    session.add(x)
                    await session.commit()
                    print("用户添加成功")
                else:
                    print("用户名重复,禁止添加")
            except Exception as e:
                print(e)
    return ("查询成功")



##查询全部用户名
@UserApp.get("/alluser")
async def AllUser():
    async with db_session() as session:
        sql = select(models.User).where(models.User.gender is not None)
        reult = await session.execute(sql)
        x = reult.scalars()
        for i in x:
            print(i.__dict__['username'],i.__dict__['UserUuid'])

    return ("查询全部用户")


@UserApp.get("/getuser")
async def GetUser(inputusername:str):
    async with db_session() as session:
        stmt = select(models.User).filter_by(username=inputusername)
        result = await session.execute(stmt)
        for row in result.scalars():
            print(row.__dict__['UserUuid'])
    return 0