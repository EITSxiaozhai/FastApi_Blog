# ----- coding: utf-8 ------
# author: YAO XU time:
import os
from fastapi import Request
from sqlalchemy.orm import sessionmaker
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, UploadFile
from sqlalchemy import select, text
from starlette.background import BackgroundTasks
import datetime
from app.Fast_blog.database.database import engine, db_session
from app.Fast_blog.model.models import Blog
import shutil

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

BlogApp = APIRouter()

templates = Jinja2Templates(directory="./Fast_blog/templates")

static_folder_path = os.path.join(os.getcwd(), "Fast_blog", "static")
BlogApp.mount("/static", StaticFiles(directory=static_folder_path), name="static")


@BlogApp.post('/blogadd')
async def BlogAdd(Addtitle: str, Addcontent: str, Addauthor: str, file: UploadFile, background_tasks: BackgroundTasks,
                  request: Request, ):
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
