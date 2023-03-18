# ----- coding: utf-8 ------
# author: YAO XU time:
import uuid

from  app.Fast_blog.database.database import engine
from app.Fast_blog.model import models
from sqlalchemy.orm import sessionmaker
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from email_validator import validate_email
from pydantic import EmailStr
from  fastapi import APIRouter

models.Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
session = SessionLocal()

UserApp = APIRouter()

templates = Jinja2Templates(directory="./Fast_blog/templates")

UserApp.mount("/static", StaticFiles(directory="./Fast_blog/static"), name="static")


def UUID_crt(UuidApi):
    x = uuid.uuid5(uuid.NAMESPACE_DNS,UuidApi)
    return x



@UserApp.get('/useradd')
async def user_index(inputusername:str,password:str,gender:bool, inputemail:EmailStr):
    try:
        newuser = models.user(gender=gender,username = inputusername,userpassword = password,UserUuid=UUID_crt(inputusername),UserEmail= inputemail)
        session.add(newuser)
        session.commit()
        session.refresh(newuser)
        print("用户数据插入成功")
    except Exception as ex:
        session.rollback()
        print("出现如下异常%s"%ex)
        print("数据库信息回滚")
    return  user_index


##查询指定用户信息
@UserApp.get('/userget')
async def user_get(inputusername:str = None):
    alluser = session.query(models.user).all()
    print(alluser)
    return "x"
