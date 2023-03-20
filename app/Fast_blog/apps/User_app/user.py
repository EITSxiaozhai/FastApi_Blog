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


def UUID_crt(UuidApi):
    UuidGenerator = uuid.uuid5(uuid.NAMESPACE_DNS,UuidApi)
    return UuidGenerator


@UserApp.get("/getuser")
async def GetUser(inputusername:str):
    async with db_session() as session:
        try:
            stmt = select(models.User).filter_by(username=inputusername)
            result = await session.execute(stmt)
            for row in result.scalars():
                x = row.__dict__['username']
                return ({"Username:":x})
        except Exception as e:
            print(e)
@UserApp.get("/")
async def query(inputname:str,inpassword:str,inEmail:EmailStr,ingender:bool):
    async with db_session() as session:
            try:
                UserQurey = await GetUser(inputusername=inputname)
                print(UserQurey['username'])
                if UserQurey != None :
                    return ({"用户已经存在,存在值为:":GetUser(inputusername=inputname)})
                elif UserQurey == None:
                    x = models.User(username=inputname,userpassword=inpassword,UserEmail=inEmail,gender=ingender,UserUuid=str((UUID_crt(inputname))))
                    session.add(x)
                    await session.commit()
                    print("用户添加成功")
                    return ({"用户添加成功,你的用户名为:":GetUser(inputusername=inputname)})
            except Exception as e:
                print(e)



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


