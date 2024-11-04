# ----- coding: utf-8 ------
# author: YAO XU time:
import datetime
import os
import random
import uuid

import jwt
from fastapi import APIRouter, Request, HTTPException, Depends, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from Fast_blog.database.databaseconnection import engine, get_db
from Fast_blog.middleware.backtasks import TokenManager, Useroauth2_scheme, verify_recaptcha, send_activation_email, \
    AliOssUpload
from Fast_blog.model import models
from Fast_blog.model.models import User, Comment, Blog
from Fast_blog.schemas.schemas import UserCredentials, UserRegCredentials

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = SessionLocal()

UserApp = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def UUID_crt(UuidApi):
    UuidGenerator = uuid.uuid5(uuid.NAMESPACE_DNS, UuidApi)
    return UuidGenerator


@UserApp.post("/check-username")
async def GetUser(request: Request,db: AsyncSession = Depends(get_db)):
        try:
            icomeuser = await request.json()
            stmt = select(models.User).filter_by(username=icomeuser['username'])
            result = await db.execute(stmt)
            row = result.scalars().first()
            if row is None:
                return {"exists": False, "data": "用户未存在"}  # 用户存在
            else:
                return {"exists": True, "data": "用户存在"}  # 用户不存在
        except Exception as e:
            print(e)


def create_jwt_token(data: dict) -> str:
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token


async def verify_password(username: str, password: str,db: AsyncSession = Depends(get_db)) -> bool:
    getusername = username
    getpassword = password
    results = await db.execute(select(User).filter(User.username == getusername))
    user = results.scalar_one_or_none()
    if user is None:
        # 用户名不存在
        raise HTTPException(status_code=401, detail="验证未通过")
    elif user.userpassword != getpassword:
        # 密码不匹配
        raise HTTPException(status_code=401, detail="验证未通过")
    else:
        return True


@UserApp.post("/putuser")
async def PutUser(file: UploadFile = File(...)):
        try:
            contents = await file.read()
            # Process the contents, e.g., upload to storage, etc.
            image_url = await AliOssUpload().upload_bitsfile_avatar(bitsfile=contents)
            # Respond with any necessary data
            print(image_url)
            return {"file_name": file.filename, "content_type": file.content_type, "image_url": image_url}
        except Exception as e:
            print(f"An error occurred: {e}")
            return {"error": "服务器发生了问题!"}


@UserApp.post("/reguser")
async def RegUser(reg: UserRegCredentials,db: AsyncSession = Depends(get_db)):
        try:

            RecaptchaResponse = await verify_recaptcha(UserreCAPTCHA=reg.googlerecaptcha, SecretKeyTypology="user")

            if RecaptchaResponse["message"]["success"]:
                sql = select(User).filter(User.username == reg.username)
                result = await db.execute(sql)
                existing_user = result.scalar()
                if existing_user:
                    # 用户名已存在
                    return {"message": "用户名已存在", "success": False}
                else:
                    sql_verification_code = select(User).filter(User.ActivationCode == reg.EmailverificationCod)
                    result_verification_code = await db.execute(sql_verification_code)
                    existing_verification_code_user = result_verification_code.scalar()
                    if existing_verification_code_user:
                        sql = update(User).where(User.ActivationCode == reg.EmailverificationCod).values(
                            username=reg.username, UserUuid=UUID_crt(UuidApi=reg.username), userpassword=reg.password,
                            UserEmail=reg.email, ActivationState='YA')
                        await db.execute(sql)
                        await db.commit()
                        return {"message": "用户已经创建", "success": True}
            else:
                return {"message": "reCAPTCHA 验证失败", "success": False}
        except Exception as e:
            print("发生了下面的错误:", {e})


@UserApp.post("/login")
async def UserLogin(x: UserCredentials,db: AsyncSession = Depends(get_db)):
        try:
            RecaptchaResponse = await verify_recaptcha(UserreCAPTCHA=x.googlerecaptcha, SecretKeyTypology="user")
            if RecaptchaResponse["message"]["success"]:
                sql = select(User).filter(User.username == x.username)
                result = await db.execute(sql)
                user = result.scalars().first()
                if user is None:
                    # 用户名不存在
                    return {"data": '用户名或者密码错误'}
                elif user.userpassword != x.password:
                    # 密码不匹配
                    return {'data': '用户名或者密码错误'}
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
            return {"error": "服务器发生了问题!"}


def generate_numeric_verification_code(length=6):
    # 生成指定长度的随机整数验证码
    return ''.join(str(random.randint(0, 9)) for _ in range(length))


##查询全部用户名
@UserApp.post("/emailcod")
async def CAPTCHAByEmail(request: Request,db: AsyncSession = Depends(get_db)):
        x = await request.json()
        print(x)
        sql = select(User).filter(User.UserEmail == x["email"])
        result = await db.execute(sql)
        verification_code = generate_numeric_verification_code()
        if result.scalars().first():
            update_sql = update(User).where(User.UserEmail == x["email"]).values(ActivationCode=verification_code)
            result = await db.execute(update_sql)
            await db.commit()
            send_activation_email.delay(email=x["email"], activation_code=verification_code)
            return {"data": 'Notification sent'}
        else:
            new_user = User(UserEmail=x["email"], ActivationCode=verification_code)
            db.add(new_user)
            await db.commit()
            return {"data": 'User added'}


##查询全部用户名
@UserApp.get("/alluser")
async def AllUser(db: AsyncSession = Depends(get_db)):
    sql = select(models.User).where(models.User.gender is not None)
    reult = await db.execute(sql)
    x = reult.scalars()
    for i in x:
        print(i.__dict__['username'], i.__dict__['UserUuid'])


async def CommentListUserNameGet(user,db: AsyncSession = Depends(get_db)):
        sql = select(User).filter(User.UserId == user)
        result = await db.execute(sql)
        for i in result.first():
            return i.username


@UserApp.post("/{vueblogid}/commentlist")
async def CommentList(vueblogid: int,db: AsyncSession = Depends(get_db)):
        try:
            sql = select(models.Comment).join(models.Blog).filter(models.Blog.BlogId == vueblogid)
            result = await db.execute(sql)
            comment_dict = {}
            for i in result.scalars().all():
                x = i.__dict__['uid']
                user = await CommentListUserNameGet(user=x)
                comment_data = {
                    'id': i.__dict__['id'],
                    'parentId': i.__dict__['parentId'],
                    'uid': i.__dict__['uid'],
                    'content': i.__dict__['content'],
                    'likes': i.__dict__['likes'],
                    'address': i.__dict__['address'],
                    "user": {"homeLink": '1', "username": f"{user}",
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
            print("Caught an exception:", repr(e))
            print("Error:", e)
            return {"error": "服务器发生了问题!"}


@UserApp.post("/token")
async def Token(Incoming: OAuth2PasswordRequestForm = Depends()):
        getusername = Incoming.username
        getpassword = Incoming.password
        if not await verify_password(getusername, getpassword):
            raise HTTPException(status_code=401, detail="验证未通过")
        token_data = {
            "username": Incoming.username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        token = create_jwt_token(data=token_data)
        return {"access_token": token, "token_type": 'Bearer', "token": token}


@UserApp.post("/commentsave/vueblogid={vueblogid}")
async def CommentSave(vueblogid: int, request: Request, token: str = Depends(Useroauth2_scheme),db: AsyncSession = Depends(get_db)):
        try:
            token = token.replace("Bearer", "").strip()
            # Verify and decode the token
            token_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user = select(User).filter(User.username == token_data["username"])
            UserResult = await db.execute(user)
            x = await request.json()
            for i in UserResult.scalars().all():
                if i:
                    sql = select(models.Blog).filter(Blog.BlogId == vueblogid)
                    result = await db.execute(sql)
                    if result.first():
                        commentUp = Comment(
                            uid=i.UserId,
                            content=x['content']['content'],
                            createTime=datetime.datetime.now(),
                            parentId=x['content']['parentId'],
                            blog_id=vueblogid
                        )
                        db.add(commentUp)
                        await db.flush()
                        await db.commit()
                        return {"data": '评论添加成功'}
                    else:
                        return {"data": "评论添加失败", "reason": "找不到对应的博客"}
                else:
                    return {"data": "评论添加失败", "reason": "用户不存在"}
        except Exception as e:
            # 处理异常
            print(str(e))
            return {"data": "评论添加失败", "code": 40002}
            # 如果用户未经过身份验证或凭据无效
        except jwt.ExpiredSignatureError:
            return {"code": 40002, "message": "Token已过期"}
        except jwt.InvalidTokenError:
            return {"code": 40003, "message": "无效的Token"}
