# ----- coding: utf-8 ------
# author: YAO XU time:
import pickle
from typing import Union

from Fast_blog.database.databaseconnection import engine, db_session
from Fast_blog.middleware.backtasks import BlogCache, aliOssUpload
from Fast_blog.model.models import Blog, BlogRating, Vote, Comment, User
from fastapi import APIRouter
from fastapi import HTTPException
from sqlalchemy import event
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

BlogApp = APIRouter()

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
