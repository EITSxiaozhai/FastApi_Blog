# ----- coding: utf-8 ------
# author: YAO XU time:
import datetime
import uuid

import requests
from pydantic import EmailStr
from sqlalchemy import select


from sqlalchemy.orm import sessionmaker, selectinload
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, HTTPException
from app.Fast_blog.database.database import engine, db_session
from app.Fast_blog.middleware.backlist import TokenManager
from app.Fast_blog.model import models
from app.Fast_blog.model.models import User, Comment ,Blog

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


@UserApp.post("/reguser")
async def query(request: Request):
    async with db_session() as session:
        try:
            x = await request.json()
            if x['username'] == '' or x['password'] == '' or x['email'] == '':
                return {'Success': 'False', 'data': '传递参数违法'}
            else:
                enddata = await session.execute(select(User).filter_by(username=x['username']))
                now = enddata.scalars().first()
                if now is None:
                    Created = User(username=x['username'],userpassword=x['password'], UserEmail=x['email'],creation_time=datetime.datetime.now(),UserUuid=UUID_crt(UuidApi=x['username']))
                    session.add(Created)
                    await  session.commit()
                    return {'Success':'True','cod':'200','data': "success"}
                else:
                    return {'Success':'False','cod': '201' ,'data':"存在重复用户。跳过创建"}
        except Exception as e:
            return {'cod':'500','data':f"我们遇到了一点问题： {e}"}


@UserApp.post("/login")
async def UserLogin(request:Request):
    async with db_session() as session:
        try:
            request_data = await request.json()
            loginusername = request_data["username"]
            loginpassword = request_data["password"]

            sql = select(User).filter(User.username == loginusername)
            result = await session.execute(sql)
            user = result.scalars().first()
            if user is None:
                # 用户名不存在
               return {"data":'Error'}
            elif user.userpassword != loginpassword:
                # 密码不匹配
                return {'data':'Error'}
            else:
                usertoken = TokenManager()
                token_data = {
                    "username": loginusername,
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                }
                token_cont =  usertoken.create_jwt_token(data=token_data)
                print(token_cont)
                return {"success":"true","message":loginusername,'token':token_cont}
        except Exception as e:
            print(f"遇到了下面的问题：{e}")
            return {"data":f'{e}'}

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



@UserApp.post("/{vueblogid}/commentlist")
async def CommentList(vueblogid:int):
    async with db_session() as session:
        sql = select(models.Comment).join(models.Blog).filter(models.Blog.BlogId == vueblogid)
        result = await session.execute(sql)
        data = {}
        for i in result.scalars().all():
            data[i.__dict__['createTime'].strftime("%Y-%m-%d %H:%M:%S")] =  {'content':i.__dict__['content'],'uid':i.__dict__['uid'],'likes':i.__dict__['likes'],'address':i.__dict__['address'],"user":{"homeLink":1,"username":i.__dict__['uid'],'avatar':i.__dict__['uid']}}
        return {'data':f"{data}"}

@UserApp.post("/{vueblogid}/commentsave")
async def CommentSave(vueblogid : int):
    async with db_session() as session:
        sql = select(models.Comment).join(models.Blog).filter(models.Blog.BlogId == vueblogid)
        result = await session.execute(sql)
        for i in result.scalars().all():
            print(i.__dict__['comment'])
            return {"data":f"{i}"}
#
# @UserApp.get("/comment/page/{pageNum}/{pageSize}")
# async def page(pageNum: int, pageSize: int, articleId: Optional[int] = None):
#     # Convert query parameters to Python function parameters
#     result = comment_service.pageByAid(pageNum, pageSize, articleId)
#     return {"data": result}
#
# @UserApp.get("/comment/replyPage/{pageNum}/{pageSize}")
# async def reply_page(pageNum: int, pageSize: int, parentId: Optional[int] = None):
#     # Convert query parameters to Python function parameters
#     result = comment_service.replyPage(pageNum, pageSize, parentId)
#     return {"data": result}
#
# @UserApp.post("/comment/save")
# async def save(commentDTO: CommentDTO):
#     # Convert request body to Python function parameter
#     result = comment_service._save(commentDTO)
#     return {"data": result}
#
# @UserApp.delete("/comment/remove/{id}")
# async def remove(id: int):
#     # Convert path parameter to Python function parameter
#     result = comment_service.removeById(id)
#     return {"data": result}
#
# @UserApp.post("/comment/liked")
# async def liked(likedDTO: LikedDTO):
#     # Convert request body to Python function parameter
#     likedDTO.uid = 1  # Set the uid as needed
#     comment_like_service.liked(likedDTO)
#     return {"data": "OK"}
#
# @UserApp.get("/comment/cidList/{uid}")
# async def cid_list(uid: int):
#     # Convert path parameter to Python function parameter
#     result = comment_like_service.cidListByUid(uid)
#     return {"data": result}