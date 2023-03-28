from celery import Celery
from celery.schedules import crontab
from  fastapi import  FastAPI,Path,Request
from  Fast_blog.database.database import engine
from celery import shared_task
from Fast_blog.model import models
from sqlalchemy.orm import sessionmaker
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.Fast_blog.database.database import engine
from Fast_blog.apps import User_app
from Fast_blog.apps import Blog_app
from Fast_blog.apps import Power_Crawl
from celery.result import AsyncResult
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
session = SessionLocal()

app = FastAPI()
app.include_router(User_app.UserApp,prefix='/user', tags=["用户"])
app.include_router(Blog_app.BlogApp,prefix='/blog',tags=["博客"])
app.include_router(Power_Crawl.PowerApp,prefix='/power', tags=["电力爬虫"])


templates = Jinja2Templates(directory="./Fast_blog/templates")

app.mount("/static", StaticFiles(directory="./Fast_blog/static"), name="static")

celery_app = Celery('tasks', broker='amqp://admin:005q8LzBwPaVA7Mb1AY9@106.14.159.61:5672/', backend='redis://:KsicwKTvK062ichw30Av@106.14.159.61:7000/3')


##创建每天12点自动执行
CELERY_BEAT_SCHEDULE = {
    'add-every-day': {
        'task': 'tasks.add',
        'schedule': crontab(hour=0, minute=0,),
    },
}


# 定义测试 Celery 任务
@celery_app.task()
def add(x, y):
     print(x + y)
     return x + y


@app.get("/")
async def root():
    result = add.delay(4,4)
    print(result)
    return {"message":"hahahah"}


