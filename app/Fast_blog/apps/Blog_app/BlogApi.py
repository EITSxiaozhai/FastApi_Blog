# ----- coding: utf-8 ------
# author: YAO XU time:
import datetime
import os
import jwt
import requests
from fastapi import  Request,Depends
from sqlalchemy.orm import sessionmaker
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter,UploadFile
from sqlalchemy import select, text
from starlette.background import BackgroundTasks
import jwt
import datetime
from fastapi import Depends
from app.Fast_blog.database.database import engine, db_session
from app.Fast_blog.model.models import Blog, User
import shutil

from app.Fast_blog.schemas.schemas import UserCredentials

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
session = SessionLocal()

BlogApp = APIRouter()

templates = Jinja2Templates(directory="./Fast_blog/templates")

static_folder_path = os.path.join(os.getcwd(), "Fast_blog", "static")
BlogApp.mount("/static", StaticFiles(directory=static_folder_path), name="static")

@BlogApp.post('/blogadd')
async def BlogAdd(Addtitle: str, Addcontent: str, Addauthor: str, file: UploadFile, background_tasks: BackgroundTasks,request: Request,):
    async with db_session() as session:
        try:
            # 将文件保存到磁盘
            file_path = os.path.join(static_folder_path, "uploadimages", file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

            base_url = str(request.base_url)
            # 构建完整的URL地址
            image_url = f"{base_url.rstrip('/')}/static/uploadimages/{file.filename}"
            # 构建参数值字典
            params = {
                "title": Addtitle,
                "content": Addcontent,
                "BlogIntroductionPicture": image_url,  # 使用完整的URL地址
                "author": Addauthor,
                "created_at": datetime.datetime.now()
            }
            # 执行插入操作
            insert_statement = text(
                "INSERT INTO blogtable (title, content, `BlogIntroductionPicture`, author, created_at) "
                "VALUES (:title, :content, :BlogIntroductionPicture, :author, :created_at)").params(**params)
            await session.execute(insert_statement)
            await session.commit()

            return {'message': '文章已经添加到对应数据库', 'image_url': image_url}

        except Exception as e:
            print("我们遇到了下面的问题", {"data": e})





##序列化输出示例代码
# @BlogApp.get("/BlogIndex")
# ##博客首页API
# async def BlogIndex():
#     async with db_session() as session:
#         try:
#             stmt = select(models.Blog).order_by(models.Blog.BlogId)
#             result = await session.execute(text("select * from blogtable LIMIT 3;"))
#             results = result.fetchall()
#             results = [tuple(row) for row in results]
#             print(f"{type(results)} of type {type(results[0])}")
#             # <class 'list'> of type <class 'tuple'>
#             json_string = json.dumps(results,ensure_ascii=False)
#             return ({"data":json_string})
#         except Exception as e:
#             print("我们遇到了下面的问题")
#             print(e)
#         return 0




@BlogApp.get("/BlogIndex")
##博客首页API
async def BlogIndex():
    async with db_session() as session:
        try:
            results = await session.execute(select(Blog).limit(10))
            data = results.scalars().all()
            data = [item.to_dict() for item in data]
            print(data)
            return (data)
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
        return 0





@BlogApp.post("/Blogid")
##博客首页API
async def Blogid(blog_id: int):
    async with db_session() as session:
        try:
            results = await session.execute(select(Blog).filter(Blog.BlogId == blog_id))
            data = results.scalars().all()
            data = [item.to_dict() for item in data]
            print(data)
            return data
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
        return []



SECRET_KEY = "eGFREkvK5zawfnNJ3DR5"
ALGORITHM = "HS256"

def create_jwt_token(data: dict) -> str:
    """
    Function to create JWT token using provided data.
    """
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token





@BlogApp.post("/user/login")
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

@BlogApp.get("/user/info")
##博客Admin token 转移
async def Userinfo():
    async with db_session() as session:
        try:
            return {"code": 20000,"data":
                {
                "roles": ["admin"],
		        "introduction": "I am a super administrator",
		        "avatar": "https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif",
		        "name": "Super Admin"
                }
                    }
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
        return 0


@BlogApp.get("/transaction/list")
##博客Admin 动态权限生成菜单
async def Userinfo():
    async with db_session() as session:
        try:
            return {"code": 20000,"data":
                {
                "roles": ["admin"],
		        "introduction": "I am a super administrator",
		        "avatar": "https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif",
		        "name": "Super Admin"
                }
                    }
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
        return 0

@BlogApp.get("/user/logout")
##博客Admin退出系统
async def UserloginOut():
    async with db_session() as session:
        try:
            return {"data":"success"}
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
        return 0