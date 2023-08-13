import uuid
import datetime

import jwt
from fastapi import APIRouter,Request
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

def create_jwt_token(data: dict) -> str:
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token


@AdminApi.post("/user/login")
##博客登录
async def UserLogin(credentials: UserCredentials):
    async with db_session() as session:
        try:
            getusername = credentials.username
            getpassword = credentials.password

            results = await session.execute(select(User).filter(User.username == getusername))
            user = results.scalar_one_or_none()
            if user is None:
                # 用户名不存在
                return "Username or Password does not exist"
            elif user.userpassword != getpassword:
                # 密码不匹配
                return "Username or Password does not exist"
            else:
                authenticated = True  # 将其替换为您实际的身份验证逻辑
                # If the user is authenticated, generate a JWT token
                if authenticated:
                    # Data to be stored in the token (can include additional claims as needed)
                    token_data = {
                        "username": getusername,
                        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                    }

                    # Generate the JWT token
                    token = create_jwt_token(token_data)

                    # Return the token along with other data in the response
                    return {
                        "code": 20000,
                        "data": {
                            "token": token,
                            "msg": "登录成功",
                            "state": "true"
                        }
                    }
            # If the user is not authenticated or invalid credentials
            return {"code": 40001, "message": "Invalid credentials"}
        # 如果用户未经过身份验证或凭据无效
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
        return 0

@AdminApi.get("/user/info")
async def Userinfo(request: Request):
    async with db_session() as session:
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
                print(privileges)

                if user:
                    return {"code": 20000, "data":
                        {
                            "roles": [f"{privileges}"],
                        }
                    }



@AdminApi.get("/transaction/list")
##博客Admin 动态权限生成菜单
async def Userinfo(request: Request):
    async with db_session() as session:
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
                print(privileges)

                if user:
                    return {"code": 20000, "data":
                        {
                            "roles": [f"{privileges}"],
                        }
                    }


@AdminApi.post("/user/adminlist")
async def AllAdminUser():
    async with db_session() as session:
        try:
            sql = select(AdminUser)
            result = await session.execute(sql)
            data = result.scalars().all()
            data = [item.to_dict() for item in data]
            return {"code": 20000,"data":data}  # Removed the extra curly
        except Exception as e:
            print(e)
            return []


def UUID_crt(UuidApi):
    UuidGenerator = uuid.uuid5(uuid.NAMESPACE_DNS,UuidApi)
    return UuidGenerator


async def GetUser(inputusername:str):
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
async def query(inputname:str,inpassword:str,inEmail:EmailStr,ingender:bool,Typeofuser:bool):
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
async def UpdateUser(request: Request):
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
async def UserPrivilegeName(request: Request):
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
