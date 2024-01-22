# ----- coding: utf-8 ------
# author: YAO XU time:
from sqlalchemy.exc import IntegrityError
import os
import pickle
from typing import Union
from sqlalchemy import event
from fastapi import Depends, Body, File
from sqlalchemy.orm import sessionmaker
from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, UploadFile
from sqlalchemy import select, text, func
from sqlalchemy import update

from fastapi import HTTPException

from app.Fast_blog.database.database import engine, db_session
from app.Fast_blog.middleware.backlist import BlogCache, Adminoauth2_scheme, aliOssUpload
from app.Fast_blog.model.models import Blog, BlogRating, Vote, Comment, User, BlogTag
from app.Fast_blog.schemas.schemas import BlogCreate

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

BlogApp = APIRouter()



static_folder_path = os.path.join(os.getcwd(), "Fast_blog", "static")
BlogApp.mount("/static", StaticFiles(directory=static_folder_path), name="static")

uploadoss = aliOssUpload()
## 博客游客用户主页显示

from sqlalchemy import func


@BlogApp.get("/blog/BlogIndex")
async def BlogIndex(initialLoad: bool = True, page: int = 1, pageSize: int = 4):
    async with db_session() as session:
        try:
            columns = [Blog.BlogId, Blog.title, Blog.created_at, Blog.author, Blog.BlogIntroductionPicture]

            # 查询实际数据库中的文章总数
            total_articles = await session.scalar(select(func.count()).select_from(Blog))

            # 根据实际数据库中的文章总数调整 pageSize
            adjusted_page_size = min(pageSize, total_articles)

            # 计算合法的 offset，确保不超过实际文章数量
            offset = (page - 1) * adjusted_page_size if page > 0 else 0
            stmt = select(*columns).offset(offset).limit(adjusted_page_size)
            results = await session.execute(stmt)
            data = results.fetchall()

            data_dicts = []
            for row in data:
                data_dict = {
                    "BlogId": row[0],
                    "title": row[1],
                    "created_at": row[2],
                    "author": row[3],
                    "BlogIntroductionPicture": row[4],
                }
                data_dicts.append(data_dict)

            return data_dicts
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
            return {"errorCode": 500}


@BlogApp.get("/blog/AdminBlogIndex")
##用户博客首页API
async def AdminBlogIndex(token: str = Depends(Adminoauth2_scheme)):
    async with db_session() as session:
        try:
            results = await session.execute(select(Blog))
            if results is not None:
                data = results.scalars().all()
                data = [item.to_dict() for item in data]
                print(data)
                return {"code": 20000, "data": data}
            else:
                return {"code": 20001, "message": "未找到数据"}
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
            return {"code": 50000, "message": "内部服务器错误"}


blog_cache = BlogCache()


# Create event listener to update cache
@event.listens_for(Blog, 'after_insert')
@event.listens_for(Blog, 'after_update')
@event.listens_for(Blog, 'after_delete')
def update_cache(mapper, connection, target):
    redis_key = f"blog_{target.BlogId}"
    data = {
        "BlogId": target.BlogId,
        "title": target.title,
        "content": target.content,
        "author": target.author,
        "BlogIntroductionPicture": target.BlogIntroductionPicture,
        "created_at": target.created_at,
    }
    blog_cache.redis_client.set(redis_key, pickle.dumps([data]))
    blog_cache.redis_client.expire(redis_key, 3600)  # Set expiration time to 1 hour


### 数据库缓存读取判断
@BlogApp.post("/user/Blogid")
async def Blogid(blog_id: int):
    async with db_session() as session:
        redis_key = f"blog_{blog_id}"
        cached_data = blog_cache.redis_client.get(redis_key)
        if cached_data:
            print('从缓存中读取')
            cached_data_obj = pickle.loads(cached_data)
            return cached_data_obj
        else:
            print('从数据库中读取')
            results = await session.execute(select(Blog).filter(Blog.BlogId == blog_id))
            data = results.scalars().all()
            data = [item.to_dict() for item in data]
            blog_cache.redis_client.set(redis_key, pickle.dumps(data))
            blog_cache.redis_client.expire(redis_key, 3600)
            return data


@BlogApp.post("/blog/Blogid")
##博客对应ID内容查询
async def AdminBlogid(blog_id: int, token: str = Depends(Adminoauth2_scheme)):
    async with db_session() as session:
        try:
            results = await session.execute(select(Blog).filter(Blog.BlogId == blog_id))
            data = results.scalars().all()
            data = [item.to_dict() for item in data]
            return {"code": 20000, "data": data}
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
        return []


@BlogApp.post("/blog/Blogeditimg")
async def AdminBlogidADDimg(blog_id: int, file: UploadFile = File(...), token: str = Depends(Adminoauth2_scheme)):
    async with db_session() as session:
        try:
            file = await file.read()
            fileurl = await uploadoss.Binaryfileupload(blogid=blog_id, bitsfile=file)
            result = await session.execute(select(Blog).filter(Blog.BlogId == blog_id))
            now = result.scalars().first()

            if now is None:
                print("数据库中还没有对应ID图片，进行新建")
                return {
                    "code": 20000,
                    "data": {
                        "msg": fileurl
                    }
                }
            else:
                print("数据库中存在对应ID图片，进行修改")
                update_stmt = update(Blog).where(Blog.BlogId == blog_id).values(BlogIntroductionPicture=fileurl)
                # 执行更新操作
                await session.execute(update_stmt)
                await session.commit()  # 提交事务以保存更改
                return {
                    "code": 20000,
                    "data": {
                        "msg": fileurl
                    }
                }

        except Exception as e:
            print(f"我们遇到了下面的错误{e}")
            return {"code": 50000, "message": "服务器错误"}


@BlogApp.post("/blog/Blogedit")
##博客对应ID编辑
async def AdminBlogidedit(blog_id: int, blog_edit: BlogCreate, token: str = Depends(Adminoauth2_scheme)):
    async with db_session() as session:
        try:
            # 提取标签信息
            tags = blog_edit.tags

            # 根据 BlogId 查询相应的博客
            result = await session.execute(select(Blog).filter(Blog.BlogId == blog_id))
            blog_entry = result.scalar_one()

            # 更新博客内容
            for key, value in blog_edit.dict().items():
                if key == 'content':
                    # 编码字符串为二进制
                    setattr(blog_entry, key, bytes(value, encoding='utf-8'))
                else:
                    setattr(blog_entry, key, value)

            # 提交事务
            await session.flush()

            blog_id = blog_entry.BlogId
            # 创建对应的博客标签
            for tag in tags:
                blog_tag = BlogTag(Article_Type=tag, blog_id=blog_id)
                session.add(blog_tag)

            await session.commit()
            return {"code": 20000, "message": "更新成功"}
        except Exception as e:
            print("遇到了问题")
            print(e)
            await session.rollback()  # 发生错误时回滚事务
            return {"code": 50000, "message": "更新失败"}
## 将数据存入数据库
@BlogApp.post("/blogs/{blog_id}/ratings/")
async def rate_blog(blog_id: str, rating: int, device_id: str):
    async with db_session() as session:
        # 检查评分是否在有效范围
        if not (1 <= rating <= 5):
            raise HTTPException(status_code=400, detail="评分必须在1到5之间")

        # 异步查询博客文章
        blog = await session.execute(select(Blog).where(Blog.BlogId == blog_id))
        blog_entry = blog.scalar_one()  # 使用 scalar_one 获取一行

        if blog_entry is None:
            raise HTTPException(status_code=404, detail="博客文章不存在")

        # 在这里将 rating 转换为整数
        rating = int(rating)

        # 查询特定设备ID对特定文章的投票次数
        vote = await session.execute(
            select(Vote).where((Vote.device_id == device_id) & (Vote.blog_id == blog_id))
        )
        vote = vote.scalar()

        if vote is not None and vote.vote_count >= 1:
            raise HTTPException(status_code=400, detail="每台设备只能投一次票")

        # 插入评分记录
        await session.execute(
            BlogRating.__table__.insert().values(
                blog_id=blog_id, rating=rating
            )
        )

        if vote is None:
            vote = Vote(device_id=device_id, blog_id=blog_id, vote_count=1)
            session.add(vote)
        else:
            vote.vote_count += 1

        await session.commit()  # 使用 await 提交更改到数据库
        return {"message": "评分成功"}


##数据库平均值取出
@BlogApp.get("/blogs/{blog_id}/average-rating/", response_model=Union[float, int])
async def get_average_rating(blog_id: int):
    async with db_session() as session:
        blog = await session.execute(select(Blog).where(Blog.BlogId == blog_id))
        if blog.scalar() is None:
            return 0  # 返回默认值 0，表示从未评分过
        average_rating = await session.execute(
            select(func.avg(BlogRating.rating)).filter(BlogRating.blog_id == blog_id)
        )
        average_rating = average_rating.scalar()
        if average_rating is not None:
            return int(round(average_rating))
        else:
            return 0  # 返回默认值 0，表示从未评分过


@BlogApp.post("/blogs/{blog_id}/submitcomments/")
async def SubmitComments(blog_id: int, comment: Comment):
    async with db_session() as session:
        user = session.query(User).filter_by(UserId=comment.uid).first()
        if user is None:
            raise HTTPException(status_code=400, detail="User not found")

        new_comment = Comment(**comment.dict(), uid=user.UserId)
        session.add(new_comment)
        session.commit()
        return {"message": "Comment submitted successfully!"}


@BlogApp.post("/blog/BlogCreate")
##博客Admin创建文章
async def AdminBlogCreate(blog_create: BlogCreate, token: str = Depends(Adminoauth2_scheme)):
    async with db_session() as session:
        try:
            content = blog_create.content.encode('utf-8')  # 将content字段转换为字节
            blog_create.content = content  # 更新blog_create中的content值

            # 提取标签信息
            tags = blog_create.tags

            # 创建博客文章
            blog_data = blog_create.dict(exclude={'tags'})  # 排除'tags'字段
            blog = Blog(**blog_data)
            session.add(blog)
            await session.flush()  # 获取插入记录后的自增值
            blog_id = blog.BlogId

            # 创建对应的博客标签
            for tag in tags:
                blog_tag = BlogTag(Article_Type=tag, blog_id=blog_id)
                session.add(blog_tag)

            await session.commit()

            return {"code": 20000, "message": "更新成功"}
        except IntegrityError as e:
            # 处理标签重复或其他数据库完整性错误
            print("数据库完整性错误:", e)
            return {"code": 40001, "message": "标签重复或其他数据库完整性错误"}
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
            return {"code": 50000, "message": "服务器错误"}

@BlogApp.post("/blog/BlogDel")
##博客Admin删除
async def AdminBlogDel(blog_id: int, token: str = Depends(Adminoauth2_scheme)):
    async with db_session() as session:
        async with session.begin():
            try:
                result = await session.execute(select(Blog).where(Blog.BlogId == blog_id))
                original = result.scalars().first()
                await    session.delete(original)
                return {"code": 20000, "message": "删除成功", "success": True}
            except Exception as e:
                print("我们遇到了下面的问题")
                print(e)
                return {"code": 50000, "message": "服务器错误", "success": False}
