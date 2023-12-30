# ----- coding: utf-8 ------
# author: YAO XU time:
import datetime
import os
import uuid

import jwt
import requests
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy import select

from sqlalchemy.orm import sessionmaker, selectinload
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.sql.functions import current_user

from app.Fast_blog.database.database import engine, db_session
from app.Fast_blog.middleware.backlist import TokenManager, Useroauth2_scheme, verify_recaptcha
from app.Fast_blog.model import models
from app.Fast_blog.model.models import User, Comment, Blog
from app.Fast_blog.schemas.schemas import CommentDTO, UserCredentials

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = SessionLocal()

UserApp = APIRouter()

templates = Jinja2Templates(directory="./Fast_blog/templates")

UserApp.mount("/static", StaticFiles(directory="./Fast_blog/static"), name="static")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
                    Created = User(username=x['username'], userpassword=x['password'], UserEmail=x['email'],
                                   creation_time=datetime.datetime.now(), UserUuid=UUID_crt(UuidApi=x['username']))
                    session.add(Created)
                    await  session.commit()
                    return {'Success': 'True', 'cod': '200', 'data': "success"}
                else:
                    return {'Success': 'False', 'cod': '201', 'data': "存在重复用户。跳过创建"}
        except Exception as e:
            return {'cod': '500', 'data': f"我们遇到了一点问题： {e}"}

def create_jwt_token(data: dict) -> str:
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token

async def verify_password(username: str, password: str) -> bool:
    async with db_session() as session:
        getusername = username
        getpassword = password
        results = await session.execute(select(User).filter(User.username == getusername))
        user = results.scalar_one_or_none()
        if user is None:
            # 用户名不存在
            raise HTTPException(status_code=401, detail="验证未通过")
        elif user.userpassword != getpassword:
            # 密码不匹配
            raise HTTPException(status_code=401, detail="验证未通过")
        else:
            return True
    # 在这里进行密码验证的逻辑，比如查询数据库，验证用户名和密码是否匹配
    # 返回 True 或 False
    # ...
    return True  # 示例中直接返回 True，您需要根据实际情况进行验证


@UserApp.post("/login")
async def UserLogin(x: UserCredentials):
    async with db_session() as session:
        try:
            RecaptchaResponse = await verify_recaptcha(UserreCAPTCHA=x.googlerecaptcha,SecretKeyTypology="user")
            if RecaptchaResponse["message"]["success"]:
                sql = select(User).filter(User.username == x.username)
                result = await session.execute(sql)
                user = result.scalars().first()
                if user is None:
                    # 用户名不存在
                    return {"data": 'Error'}
                elif user.userpassword != x.password:
                    # 密码不匹配
                    return {'data': 'Error'}
                else:
                    usertoken = TokenManager()
                    token_data = {
                        "username": x.username,
                        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                    }
                    token_cont = usertoken.create_jwt_token(data=token_data)
                    print(token_cont)
                    return {"success": "true", "message": x.username, 'token': token_cont}
        except Exception as e:
            print(f"遇到了下面的问题：{e}")
            return {"data": f'{e}'}


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
async def CommentList(vueblogid: int):
    async with db_session() as session:
        try:
            sql = select(models.Comment).join(models.Blog).filter(models.Blog.BlogId == vueblogid)
            result = await session.execute(sql)
            comment_dict = {}

            for i in result.scalars().all():
                comment_data = {
                    'id': i.__dict__['id'],
                    'parentId': i.__dict__['parentId'],
                    'uid': i.__dict__['uid'],
                    'content': i.__dict__['content'],
                    'likes': i.__dict__['likes'],
                    'address': i.__dict__['address'],
                    "user": {"homeLink": '1', "username": i.__dict__['uid'],
                             'avatar': "https://api.vvhan.com/api/avatar"},
                    'reply': {'total': 0, 'list': []}
                }

                if i.__dict__['parentId'] is None:
                    comment_dict[i.__dict__['id']] = comment_data
                else:
                    parent_id = i.__dict__['parentId']
                    if parent_id in comment_dict:
                        comment_dict[parent_id]['reply']['list'].append(comment_data)
                        comment_dict[parent_id]['reply']['total'] += 1

            return list(comment_dict.values())

        except Exception as e:
            return {"error": f"commentlist {e}"}



@UserApp.post("/token")
async def Token(Incoming: OAuth2PasswordRequestForm = Depends()):
    async with db_session() as session:
        getusername = Incoming.username
        getpassword = Incoming.password
        if not await verify_password(getusername, getpassword):
            raise HTTPException(status_code=401, detail="验证未通过")
        # print(getusername)
        # results = await session.execute(select(AdminUser).filter(AdminUser.username == getusername))
        # user = results.scalar_one_or_none()
        # if user is None:
        #     # 用户名不存在
        #     raise HTTPException(status_code=401, detail="验证未通过")
        # elif user.userpassword != getpassword:
        #     # 密码不匹配
        #     raise HTTPException(status_code=401, detail="验证未通过")
        # else:
        token_data = {
            "username": Incoming.username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        token = create_jwt_token(data=token_data)
        return {"access_token": token, "token_type": 'Bearer', "token": token}


@UserApp.post("/{vueblogid}/commentsave")
async def CommentSave(vueblogid: int, request: Request,token: str = Depends(Useroauth2_scheme)):
    async with db_session() as session:
        try:
            token = token.replace("Bearer", "").strip()
            # Verify and decode the token
            token_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user = select(User).filter(User.username == token_data["username"])
            UserResult = await session.execute(user)
            x = await request.json()
            for i in UserResult.scalars().all():
                if i:
                    sql = select(models.Comment).join(models.Blog).filter(models.Blog.BlogId == vueblogid)
                    result = await session.execute(sql)
                    if result.first() is not None:
                        commentUp = Comment(
                            uid=  i.UserId,
                            content=x['content']['content'],
                            createTime=datetime.datetime.now(),
                            parentId=x['content']['parentId'],
                            blog_id=vueblogid
                        )
                        session.add(commentUp)
                        await session.flush()
                        await session.commit()
                        return {"data":'评论添加成功'}
                    else:
                        return {"data": "评论添加失败"}
                else:
                        return {"data":"评论添加失败"}
            # 如果用户未经过身份验证或凭据无效
        except jwt.ExpiredSignatureError:
            return {"code": 40002, "message": "Token已过期"}
        except jwt.InvalidTokenError:
            return {"code": 40003, "message": "无效的Token"}
