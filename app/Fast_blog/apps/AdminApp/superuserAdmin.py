import uuid
import datetime
from http.client import HTTPException
from typing import Annotated

import httpx
import jwt
from fastapi import APIRouter, Request, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.Fast_blog.database.database import db_session
from app.Fast_blog.model import models
from app.Fast_blog.model.models import AdminUser, User, UserPrivileges
from app.Fast_blog.schemas.schemas import UserCredentials

AdminApi = APIRouter()



SECRET_KEY = "d81beb2748aa1322fe038c26dbd263907f5808548f9e428f4d9ce780dd4358a6cc942a1ee8bd49652991bce4989e270c55adeb0c5138ff516de13a07a5bdd5be"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")


def create_jwt_token(data: dict) -> str:
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token

@AdminApi.post("/token")
async def Token(Incoming:OAuth2PasswordRequestForm = Depends()):
    async with db_session() as session:
        getusername = Incoming.username
        getpassword = Incoming.password
        print(getusername)
        results = await session.execute(select(AdminUser).filter(AdminUser.username == getusername))
        user = results.scalar_one_or_none()
        if user is None:
            # 用户名不存在
            return {"data":"UsernameError"}
        elif user.userpassword != getpassword:
            # 密码不匹配
            return {"data":"UsernameOrPasswordError"}
        else:
            token_data = {
                "username": Incoming.username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }
            # Generate the JWT token
            token = create_jwt_token(token_data)
            return {"token":token}



@AdminApi.post("/user/login")
##博客登录
async def UserLogin(x:UserCredentials):
    async with db_session() as session:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post("http://127.0.0.1:8000/api/token", data={"username": x.username, "password": x.password})
                token_data = response.json()
                if "token" in token_data:
                    return {
                        "code": 20000,
                        "data": {
                            "token": token_data["token"],
                            "msg": "登录成功",
                            "state": "true"
                        }
                    }
            return {"code": 40001, "message": "Invalid credentials"}
        # 如果用户未经过身份验证或凭据无效
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
            return {"code": 50000, "message": "内部服务器错误"}
        except jwt.ExpiredSignatureError:
            return {"code": 40002, "message": "Token已过期"}
        except jwt.InvalidTokenError:
            return {"code": 40003, "message": "无效的Token"}

@AdminApi.get("/user/info")
async def Userinfo(request: Request):
    async with db_session() as session:
        try:
            # Get the token from the request headers
            token = request.headers.get("Authorization")

            if token:
                token = token.replace("Bearer", "").strip()

                # Verify and decode the token
                token_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

                username = token_data.get("username")
                if username:
                    stmt = select(models.AdminUser).join(models.UserPrivileges).add_columns(
                        models.UserPrivileges.privilegeName).filter(
                        models.AdminUser.username == username
                    )
                    result = await db_session.execute(stmt)
                    user, privileges  = result.fetchone()

                    if user:
                        return {"code": 20000, "data":
                            {
                                "roles": [f"{privileges}"],
                            }
                        }
            return {"code": 20001, "message": "用户未找到"}
        except jwt.ExpiredSignatureError:
            return {"code": 40002, "message": "Token已过期"}
        except jwt.InvalidTokenError:
            return {"code": 40003, "message": "无效的Token"}
        except Exception as e:
            print("博客Admin token 转移我们遇到了下面的问题")
            print(e)
            return {"code": 50000, "message": "内部服务器错误"}



@AdminApi.get("/transaction/list")
##博客Admin 动态权限生成菜单
async def Userinfo(request: Request):
    async with db_session() as session:
        try:
            # Get the token from the request headers
            token = request.headers.get("Authorization")

            if token:
                token = token.replace("Bearer", "").strip()

                # Verify and decode the token
                token_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

                username = token_data.get("username")
                if username:
                    stmt = select(models.AdminUser).join(models.UserPrivileges).add_columns(
                        models.UserPrivileges.privilegeName).filter(
                        models.AdminUser.username == username
                    )
                    result = await db_session.execute(stmt)
                    user, privileges  = result.fetchone()
                    if user:
                        return {"code": 20000, "data":
                            {
                                "roles": [f"{privileges}"],
                            }
                        }
            return {"code": 20001, "message": "用户未找到"}
        except jwt.ExpiredSignatureError:
            return {"code": 40002, "message": "Token已过期"}
        except jwt.InvalidTokenError:
            return {"code": 40003, "message": "无效的Token"}
        except Exception as e:
            print("动态菜单鉴权我们遇到了下面的问题")
            print(e)
            return {"code": 50000, "message": "内部服务器错误"}


@AdminApi.post("/user/adminlist")
async def AllAdminUser(token: str = Depends(oauth2_scheme)):
    async with db_session() as session:
        try:
            sql = select(AdminUser)
            result = await session.execute(sql)
            data = result.scalars().all()

            modified_data = []
            for item in data:
                user_privilege = await session.scalar(
                    select(UserPrivileges.privilegeName)
                    .where(UserPrivileges.NameId == item.userPrivileges)
                )
                if user_privilege is not None:
                    item_dict = item.to_dict()
                    item_dict["privilegeName"] = user_privilege
                    modified_data.append(item_dict)
            return {"code": 20000, "data": modified_data}
        except jwt.ExpiredSignatureError:
            return {"code": 40002, "message": "Token已过期"}
        except jwt.InvalidTokenError:
            return {"code": 40003, "message": "无效的Token"}
        except Exception as e:
            return {"code": 50000, "message": "内部服务器错误"}


def UUID_crt(UuidApi):
    UuidGenerator = uuid.uuid5(uuid.NAMESPACE_DNS,UuidApi)
    return UuidGenerator


async def GetUser(inputusername:str,token: str = Depends(oauth2_scheme)):
    async with db_session() as session:
        try:
            stmt = select(models.AdminUser).filter_by(username=inputusername)
            result = await session.execute(stmt)
            for row in result.scalars():
                x = row.__dict__['username']
                return ({"Username:":x})
        except Exception as e:
            print(e)


@AdminApi.get("/Adminadd")
async def query(inputname:str,inpassword:str,inEmail:EmailStr,ingender:bool,Typeofuser:bool,token: str = Depends(oauth2_scheme)):
    async with db_session() as session:
            try:
                UserQurey = await GetUser(inputusername=inputname)
                if UserQurey != None :
                    return ({"用户已经存在,存在值为:":UserQurey['username']})
                elif UserQurey == None:
                    x = models.AdminUser(username=inputname,userpassword=inpassword,UserEmail=inEmail,gender=ingender,userPrivileges=Typeofuser,UserUuid=str((UUID_crt(inputname))))
                    session.add(x)
                    await session.commit()
                    print("用户添加成功")
                    return ({"用户添加成功,你的用户名为:":inputname})
            except Exception as e:
                print(e)
            return {"重复用户名":UserQurey}

@AdminApi.post("/user/updateUser")
async def UpdateUser(request: Request,token: str = Depends(oauth2_scheme)):
    async with db_session() as session:
        try:
            data = await request.json()  # This will extract the JSON data from the request body
            stmt = select(models.AdminUser).filter_by(
                username=data["username"])  # Assuming "username" is the primary key
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                # Update the user's information based on the received data
                user.UserEmail = data["UserEmail"]
                user.UserUuid = data["UserUuid"]
                user.gender = data["gender"]["code"]
                # user.Typeofuser = data["Typeofuser"]["code"]
                await session.commit()
                return {"code":20000}
            else:
                return {"data": "User not found"}
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
        return 0

@AdminApi.post("/user/getTypeofuserData")
##博客Admin权限管理
async def UserPrivilegeName(request: Request,token: str = Depends(oauth2_scheme)):
    async with db_session() as session:
        try:
            data = await request.json()
            stmt = select(models.AdminUser).filter_by(usename=data['username'])  # Assuming "username" is the primary key
            stmt = stmt.options(joinedload(AdminUser.userPrivileges))
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            if user:
                privilege = user.userPrivileges.privilegeName
                return {"code": 20000, "privilegeName": privilege}
            else:
                return {"code": 20001, "message": "User not found"}
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
        return {"code": 20001, "message": "User not found"}


@AdminApi.get("/user/logout")
##博客Admin退出系统
async def UserloginOut():
    async with db_session() as session:
        try:
            return {"data":"success"}
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
        return 0
