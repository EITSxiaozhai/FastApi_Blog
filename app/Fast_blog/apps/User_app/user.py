# ----- coding: utf-8 ------
# author: YAO XU time:

from  app.Fast_blog.database.database import engine
from app.Fast_blog.model import models
from sqlalchemy.orm import sessionmaker
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from  fastapi import APIRouter

models.Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
session = SessionLocal()

UserApp = APIRouter()

templates = Jinja2Templates(directory="./Fast_blog/templates")

UserApp.mount("/static", StaticFiles(directory="./Fast_blog/static"), name="static")


@UserApp.get('/useradd')
def user_index(username:str = None,password:str = None,gender:bool = None):
    newuser = models.user(gender=gender,username = username,userpassword = password)
    session.add(newuser)
    session.commit()
    session.refresh(newuser)
    print("hahahah")
    return  newuser


##查询指定用户信息
@UserApp.get('/userget')
async def user_get(username:str = None):
    y = session.query(models.user).filter(models.user.username == username)
    for i in y:
        print(i.Last_Login_Time)
    return "x"
