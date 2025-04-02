# ----- coding: utf-8 ------
# author: YAO XU time:
import asyncio
import json
import pickle
from typing import Union

import pytz
import redis
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
import aiohttp
from datetime import datetime
import random

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
        # 查询数据库中发布状态为1的文章总数
        total_articles = await db.scalar(select(func.count()).select_from(Blog).where(Blog.PublishStatus == 1))
        # 确保pageSize不超过实际文章总数，避免无效查询
        adjusted_page_size = min(pageSize, total_articles) if total_articles > 0 else 0
        # 计算offset，确保合理的分页
        offset = max((page - 1) * adjusted_page_size, 0)  # 保证offset不为负值
        # 添加查询条件，仅查询发布状态为1的文章
        stmt = select(*columns).where(Blog.PublishStatus == 1).offset(offset).limit(adjusted_page_size)
        results = await db.execute(stmt)
        data = results.fetchall()
        data_dicts = []
        for row in data:
            taglist = await GetBlogTaginfo(blog_id=row[0])  # 补充获取标签信息

            # 时间处理部分转换为当地时间
            utc_time = row[2]
            local_tz = pytz.timezone('Asia/Shanghai')
            local_time = utc_time.astimezone(local_tz)
            formatted_time = local_time.strftime('%Y-%m-%d')

            # 构造输出字典
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
        return {"errorCode": 500, "message": str(e)}


blog_cache = BlogCache()


# 添加FastAPI生命周期事件
@BlogApp.on_event("startup")
async def startup_event():
    await blog_cache.initialize()
    print("Redis缓存已初始化" if blog_cache.is_ready() else "Redis初始化失败")


# 改进版ORM事件监听
@event.listens_for(Blog, 'after_insert')
@event.listens_for(Blog, 'after_update')
@event.listens_for(Blog, 'after_delete')
def update_cache(mapper, connection, target):
    """同步事件触发异步任务"""
    redis_key = f"blog:{target.BlogId}"

    # 将更新操作提交到后台任务队列
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(async_cache_update(redis_key, target))
    else:
        asyncio.run(async_cache_update(redis_key, target))


async def async_cache_update(redis_key: str, blog: Blog):
    """实际执行缓存更新的异步方法"""
    if not blog_cache.is_ready():
        return

    print(blog)

    data = {
        "BlogId": blog.BlogId,
        "title": blog.title,
        "content": blog.content,
        "author": blog.author,
        "BlogIntroductionPicture": blog.BlogIntroductionPicture,
        "created_at": blog.created_at.isoformat(),
    }

    try:
        # 使用管道批量操作
        async with blog_cache.redis_client.pipeline() as pipe:
            await pipe.set(redis_key, json.dumps(data))  # JSON序列化
            await pipe.expire(redis_key, 86400)
            await pipe.execute()
        print(f"成功更新缓存: {redis_key}")
    except Exception as e:
        print(f"缓存更新失败: {str(e)}")


# 增强版缓存同步任务
async def update_redis_cache(db: AsyncSession = Depends(get_db)):
    print("启动全量缓存同步")
    try:
        result = await db.execute(select(Blog))
        blogs = result.scalars().all()

        # 批量管道操作
        if blog_cache.is_ready():
            async with blog_cache.redis_client.pipeline() as pipe:
                for blog in blogs:
                    data = {
                        "BlogId": blog.BlogId,
                        "title": blog.title,
                        # ...其他字段...
                    }
                    redis_key = f"blog:{blog.BlogId}"
                    pipe.set(redis_key, json.dumps(data))
                    pipe.expire(redis_key, 86400)
                await pipe.execute()
        return {"status": f"同步完成，处理{len(blogs)}条记录"}
    except Exception as e:
        print(f"全量同步失败: {str(e)}")
        return {"status": "同步失败"}


# 改进版缓存读取接口
@BlogApp.post("/user/Blogid")
async def Blogid(blog_id: int, db: AsyncSession = Depends(get_db)):
    redis_key = f"blog:{blog_id}"

    # 尝试读取缓存
    cached_data = None
    if blog_cache.is_ready():
        try:
            cached_data = await blog_cache.redis_client.get(redis_key)
        except Exception as e:
            print(f"缓存读取异常: {str(e)}")

    if cached_data:
        print(f'缓存命中 ID: {blog_id}')
        return json.loads(cached_data)

    # 缓存未命中时查询数据库
    try:
        result = await db.execute(
            select(Blog).where(Blog.BlogId == blog_id, Blog.PublishStatus == 1)
        )
        blog = result.scalars().first()

        if not blog:
            raise HTTPException(status_code=404, detail="内容不存在")

        response_data = blog.to_dict()

        # 异步更新缓存
        if blog_cache.is_ready():
            try:
                await blog_cache.redis_client.set(
                    redis_key,
                    json.dumps(response_data),
                    ex=3600
                )
            except Exception as e:
                print(f"缓存写入失败: {str(e)}")

        return response_data
    except Exception as e:
        print(f"数据库查询失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

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
async def SubmitComments(blog_id: int, comment: dict, db: AsyncSession = Depends(get_db)):
    # 使用 select() 创建选择语句
    stmt = select(User).filter(User.UserId == comment['uid'])
    result = await db.execute(stmt)
    user = result.scalars().first()

    if user is None:
        raise HTTPException(status_code=400, detail="User not found")

    # 将 comment 字典中的数据传递给 Comment 实例化
    new_comment = Comment(**comment, uid=user.UserId)
    # 添加新评论到会话
    db.add(new_comment)
    # 提交事务
    await db.commit()

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


@BlogApp.get("/blogs/search")
async def get_blogs(q: str, db: AsyncSession = Depends(get_db)):
    # 使用过滤条件和排序
    sql = select(Blog).filter(Blog.title.ilike(f"%{q}%")).order_by(Blog.title.asc())
    result = await db.execute(sql)
    blogs = result.scalars().all()
    # 将每个 Blog 对象转换为字典
    return [blog.to_dict() for blog in blogs]

@BlogApp.get("/blogs/bing-wallpaper")
async def get_bing_wallpaper(is_random: bool = False):
    """获取Bing每日UHD壁纸
    Args:
        is_random: 是否随机获取历史图片
    """
    try:
        # 添加时间戳防止缓存
        timestamp = int(datetime.now().timestamp() * 1000)
        # 获取最近8天的图片
        url = f"https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=8&nc={timestamp}&pid=hp"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'images' in data and len(data['images']) > 0:
                        # 如果is_random为True，随机选择一张图片
                        image = data['images'][random.randint(0, len(data['images'])-1)] if is_random else data['images'][0]
                        # 直接替换为UHD格式
                        image_url = f"https://cn.bing.com{image['url'].replace('1920x1080', 'UHD')}"
                        return {
                            "code": 20000,
                            "data": {
                                "url": image_url,
                                "title": image.get('title', ''),
                                "copyright": image.get('copyright', ''),
                                "date": image.get('startdate', datetime.now().strftime('%Y-%m-%d')),
                                "is_random": is_random,
                                "resolution": "UHD"
                            }
                        }
                    else:
                        return {"code": 40000, "message": "未找到图片"}
                else:
                    return {"code": 50000, "message": "获取图片失败"}
    except Exception as e:
        return {"code": 50000, "message": f"服务器错误: {str(e)}"}