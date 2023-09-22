# ----- coding: utf-8 ------
# author: YAO XU time:
import datetime
import uuid


from pydantic import EmailStr
from sqlalchemy import select

from app.Fast_blog.database.database import engine
from sqlalchemy.orm import sessionmaker
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, HTTPException
from app.Fast_blog.database.database import db_session
from app.Fast_blog.middleware.backlist import TokenManager
from app.Fast_blog.model import models
from app.Fast_blog.model.models import User

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = SessionLocal()

UserApp = APIRouter()

templates = Jinja2Templates(directory="./Fast_blog/templates")

UserApp.mount("/static", StaticFiles(directory="./Fast_blog/static"), name="static")


def UUID_crt(UuidApi):
    UuidGenerator = uuid.uuid5(uuid.NAMESPACE_DNS, UuidApi)
    return UuidGenerator


@UserApp.get("/getuser")
async def GetUser(inputusername: str):
    async with db_session() as session:
        try:
            stmt = select(models.User).filter_by(username=inputusername)
            result = await session.execute(stmt)
            for row in result.scalars():
                x = row.__dict__['username']
                return ({"Username:": x})
        except Exception as e:
            print(e)


@UserApp.get("/reguser")
async def query(inputname: str, inpassword: str, inEmail: EmailStr, ingender: bool):
    async with db_session() as session:
        try:
            UserQurey = await GetUser(inputusername=inputname)
            if UserQurey != None:
                return ({"用户已经存在,存在值为:": UserQurey['username']})
            elif UserQurey == None:
                x = models.User(username=inputname, userpassword=inpassword, UserEmail=inEmail, gender=ingender,
                                UserUuid=str((UUID_crt(inputname))))
                session.add(x)
                await session.commit()
                print("用户添加成功")
                return ({"用户添加成功,你的用户名为:": inputname})
        except Exception as e:
            print(e)
        return {"重复用户名": UserQurey}


@UserApp.post("/login")
async def UserLogin(request:Request):
    async with db_session() as session:
        request_data = await request.json()
        loginusername = request_data["username"]
        loginpassword = request_data["password"]
        sql = select(User).filter(User.username == loginusername)
        result = await session.execute(sql)
        user = result.scalar_one_or_none()
        if user is None:
            # 用户名不存在
            raise HTTPException(status_code=401, detail="验证未通过")
        elif user.userpassword != loginpassword:
            # 密码不匹配
            raise HTTPException(status_code=401, detail="验证未通过")
        else:
            usertoken = TokenManager()
            token_data = {
                "username": loginusername,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }
            token_cont =  usertoken.create_jwt_token(data=token_data)
            return {"success":"true","message":loginusername,'token':token_cont}

##查询全部用户名
@UserApp.get("/alluser")
async def AllUser():
    async with db_session() as session:
        sql = select(models.User).where(models.User.gender is not None)
        reult = await session.execute(sql)
        x = reult.scalars()
        for i in x:
            print(i.__dict__['username'], i.__dict__['UserUuid'])
    return ("查询全部用户")
