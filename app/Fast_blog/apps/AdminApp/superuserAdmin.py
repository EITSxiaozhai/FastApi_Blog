import uuid
import datetime

import jwt
from fastapi import APIRouter
from pydantic import EmailStr
from sqlalchemy import select

from app.Fast_blog.database.database import db_session
from app.Fast_blog.model import models
from app.Fast_blog.model.models import AdminUser, User
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
##博客Admin token 转移
async def Userinfo():
    async with db_session() as session:
        try:
            return {"code": 20000,"data":
                {
                "roles": ["admin"],
                }
                    }
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
        return 0


@AdminApi.get("/transaction/list")
##博客Admin 动态权限生成菜单
async def Userinfo():
    async with db_session() as session:
        try:
            return {"code": 20000,"data":
                {
                "roles": ["admin"],
                }
                    }
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
        return 0


@AdminApi.post("/user/adminlist")
async def AllAdminUser():
    async with db_session() as session:
        try:
            sql = select(AdminUser)
            result = await session.execute(sql)
            data = result.scalars().all()
            data = [item.to_dict() for item in data]
            return {"code": 20000, "data": data}  # Removed the extra curly
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
                    x = models.AdminUser(username=inputname,userpassword=inpassword,UserEmail=inEmail,gender=ingender,Typeofuser=Typeofuser,UserUuid=str((UUID_crt(inputname))))
                    session.add(x)
                    await session.commit()
                    print("用户添加成功")
                    return ({"用户添加成功,你的用户名为:":inputname})
            except Exception as e:
                print(e)
            return {"重复用户名":UserQurey}


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
