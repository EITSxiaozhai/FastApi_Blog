# ----- coding: utf-8 ------
# author: YAO XU time:
import json
import pickle
from typing import Union

import pytz
from fastapi import APIRouter, Depends
from fastapi import HTTPException
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
)
from google.auth.exceptions import GoogleAuthError
from google.oauth2 import service_account
from sqlalchemy import event
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Fast_blog.database.databaseconnection import db_session, get_db
from Fast_blog.middleware.backtasks import AliOssPrivateDocument
from Fast_blog.middleware.backtasks import BlogCache, AliOssUpload
from Fast_blog.model.models import Blog, BlogRating, Vote, Comment, User, BlogTag

BlogApp = APIRouter()
aliOssPrivateDocument = AliOssPrivateDocument()
uploadoss = AliOssUpload()


## 博客游客用户主页显示


async def GetBlogTaginfo(blog_id: int):
    async with db_session() as session:
        taglist = []
        # 修改查询，仅选择 Article_Type 字段
        query = select(BlogTag.Article_Type).where(BlogTag.blog_id == blog_id)
        # 执行查询
        result = await session.execute(query)
        # 提取查询结果中的 Article_Type 数据
        article_types = result.scalars().all()
        # 将查询结果添加到 taglist 中
        taglist.extend(article_types)  # 将所有 Article_Type 数据加入到 taglist
        return taglist


@BlogApp.get("/blog/BlogIndex")
async def BlogIndex(initialLoad: bool = True, page: int = 1, pageSize: int = 4, db: AsyncSession = Depends(get_db)):
    try:
        columns = [Blog.BlogId, Blog.title, Blog.created_at, Blog.author, Blog.BlogIntroductionPicture]
        # 查询实际数据库中的文章总数
        total_articles = await db.scalar(select(func.count()).select_from(Blog))
        # 根据实际数据库中的文章总数调整 pageSize
        adjusted_page_size = min(pageSize, total_articles)
        # 计算合法的 offset，确保不超过实际文章数量
        offset = (page - 1) * adjusted_page_size if page > 0 else 0
        stmt = select(*columns).offset(offset).limit(adjusted_page_size)
        results = await db.execute(stmt)
        data = results.fetchall()
        data_dicts = []
        for row in data:
            taglist = await GetBlogTaginfo(blog_id=row[0])

            utc_time = row[2]
            local_tz = pytz.timezone('Asia/Shanghai')
            local_time = utc_time.astimezone(local_tz)
            formatted_time = local_time.strftime('%Y-%m-%d')

            data_dict = {
                "BlogId": row[0],
                "title": row[1],
                "created_at": formatted_time,
                "author": row[3],
                "BlogIntroductionPicture": row[4],
                "tag": taglist,
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
    print(f"刷新了缓存{target.BlogId}")
    data = {
        "BlogId": target.BlogId,
        "title": target.title,
        "content": target.content,
        "author": target.author,
        "BlogIntroductionPicture": target.BlogIntroductionPicture,
        "created_at": target.created_at,
    }

    blog_cache.redis_client.set(redis_key, pickle.dumps([data]))
    blog_cache.redis_client.expire(redis_key, 86400)  # Set expiration time to 24 hour


# 定时同步任务
async def update_redis_cache(db: AsyncSession = Depends(get_db)):
    print("开始同步")
    results = await db.execute(select(Blog))
    blogs = results.scalars().all()

    # Prepare data for blogs
    blog_data = []
    for blog in blogs:
        data = {
            "BlogId": blog.BlogId,
            "title": blog.title,
            "content": blog.content,
            "author": blog.author,
            "BlogIntroductionPicture": blog.BlogIntroductionPicture,
            "created_at": blog.created_at,
        }
        blog_data.append((f"blog_{blog.BlogId}", data))

    # Sync Blogs to Redis
    for redis_key, data in blog_data:
        blog_cache.redis_client.set(redis_key, pickle.dumps([data]))
        blog_cache.redis_client.expire(redis_key, 86400)  # Set expiration time to 24 hours


### 数据库缓存读取判断
@BlogApp.post("/user/Blogid")
async def Blogid(blog_id: int, db: AsyncSession = Depends(get_db)):
    redis_key = f"blog_{blog_id}"
    cached_data = blog_cache.redis_client.get(redis_key)
    if cached_data:
        print('从缓存中读取')
        cached_data_obj = pickle.loads(cached_data)
        return cached_data_obj
    else:
        print('从数据库中读取')
        results = await db.execute(select(Blog).filter(Blog.BlogId == blog_id))
        data = results.scalars().all()
        data = [item.to_dict() for item in data]
        blog_cache.redis_client.set(redis_key, pickle.dumps(data))
        blog_cache.redis_client.expire(redis_key, 3600)
        return data


## 将数据存入数据库
@BlogApp.post("/blogs/{blog_id}/ratings/")
async def rate_blog(blog_id: str, rating: int, device_id: str, db: AsyncSession = Depends(get_db)):
    # 检查评分是否在有效范围
    if not (1 <= rating <= 5):
        raise HTTPException(status_code=400, detail="评分必须在1到5之间")

    # 异步查询博客文章
    blog = await db.execute(select(Blog).where(Blog.BlogId == blog_id))
    blog_entry = blog.scalar_one()  # 使用 scalar_one 获取一行

    if blog_entry is None:
        raise HTTPException(status_code=404, detail="博客文章不存在")

    # 在这里将 rating 转换为整数
    rating = int(rating)

    # 查询特定设备ID对特定文章的投票次数
    vote = await db.execute(
        select(Vote).where((Vote.device_id == device_id) & (Vote.blog_id == blog_id))
    )
    vote = vote.scalar()

    if vote is not None and vote.vote_count >= 1:
        raise HTTPException(status_code=400, detail="每台设备只能投一次票")

    # 插入评分记录
    await db.execute(
        BlogRating.__table__.insert().values(
            blog_id=blog_id, rating=rating
        )
    )

    if vote is None:
        vote = Vote(device_id=device_id, blog_id=blog_id, vote_count=1)
        db.add(vote)
    else:
        vote.vote_count += 1

    await db.commit()  # 使用 await 提交更改到数据库
    return {"message": "评分成功"}


##数据库平均值取出
@BlogApp.get("/blogs/{blog_id}/average-rating/", response_model=Union[float, int])
async def get_average_rating(blog_id: int, db: AsyncSession = Depends(get_db)):
    blog = await db.execute(select(Blog).where(Blog.BlogId == blog_id))
    if blog.scalar() is None:
        return 0  # 返回默认值 0，表示从未评分过
    average_rating = await db.execute(
        select(func.avg(BlogRating.rating)).filter(BlogRating.blog_id == blog_id)
    )
    average_rating = average_rating.scalar()
    if average_rating is not None:
        return int(round(average_rating))
    else:
        return 0  # 返回默认值 0，表示从未评分过


@BlogApp.post("/blogs/{blog_id}/submitcomments/")
async def SubmitComments(blog_id: int, comment: Comment, db: AsyncSession = Depends(get_db)):
    user = db.query(User).filter_by(UserId=comment.uid).first()
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")

    new_comment = Comment(**comment.dict(), uid=user.UserId)
    db.add(new_comment)
    db.commit()
    return {"message": "Comment submitted successfully!"}


@BlogApp.get("/blogs/total_uvpv")
async def get_total_uvpv():
    try:
        # 从阿里云 OSS 获取 Google Analytics 密钥
        jsonkey = AliOssPrivateDocument()
        JSON_KEY_FILE = jsonkey.GoogleAnalytics()
        JSON_KEY_FILE_dict = json.loads(JSON_KEY_FILE.decode('utf-8'))

        credentials = service_account.Credentials.from_service_account_info(JSON_KEY_FILE_dict)
        scoped_credentials = credentials.with_scopes(
            ['https://www.googleapis.com/auth/analytics.readonly']
        )

        property_id = "457560039"  # GA4 属性 ID

        # 使用传递的凭据创建客户端
        client = BetaAnalyticsDataClient(credentials=scoped_credentials)

        # 构造查询请求：获取全站数据
        request = RunReportRequest(
            property=f'properties/{property_id}',  # 替换为你的 GA4 属性 ID
            dimensions=[],  # 不需要按维度拆分数据，获取整体数据
            metrics=[{'name': 'activeUsers'}, {'name': 'screenPageViews'}],  # UV 和 PV 指标
            date_ranges=[{'start_date': '2024-08-01', 'end_date': 'today'}]  # 建站日期到今天
        )

        response = client.run_report(request=request)

        # 初始化 UV 和 PV 数据
        total_uv = 0
        total_pv = 0

        # 提取 UV 和 PV 数据
        for row in response.rows:
            total_uv = row.metric_values[0].value
            total_pv = row.metric_values[1].value

        # 返回总 UV 和 PV
        return {
            "data": {
                "UV": total_uv,
                "PV": total_pv
            },
            "code": 20000
        }
    except GoogleAuthError as auth_error:
        return {"error": "Authentication failed", "message": str(auth_error), "code": 40002}
    except Exception as e:
        return {"error": "Internal Server Error", "message": str(e), "code": 50000}
