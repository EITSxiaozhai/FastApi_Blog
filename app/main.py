import asyncio

import anyio
from celery import Celery
from celery.schedules import crontab
from  fastapi import  FastAPI,Path,Request
from starlette.responses import JSONResponse

from  Fast_blog.database.database import engine
from celery import shared_task
from Fast_blog.model import models
from sqlalchemy.orm import sessionmaker
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from concurrent.futures import Future
from app.Fast_blog.BackList.backlist import celery_app
from app.Fast_blog.database.database import engine
from Fast_blog.apps import User_app
from Fast_blog.apps import Blog_app
from Fast_blog.apps import Power_Crawl
from Fast_blog.apps.Power_Crawl import LetView
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
session = SessionLocal()

app = FastAPI()


app.include_router(User_app.UserApp,prefix='/user', tags=["用户"])
app.include_router(Blog_app.BlogApp,prefix='/blog',tags=["博客"])
app.include_router(Power_Crawl.PowerApp,prefix='/power', tags=["电力爬虫"])


templates = Jinja2Templates(directory="./Fast_blog/templates")

app.mount("/static", StaticFiles(directory="./Fast_blog/static"), name="static")



@app.get("/")
async def root():
     response_data = {"message": "hahahah"}
     return JSONResponse(content=response_data)



@app.get("/test")
@celery_app.task(acks_late=True)
def add_to_db_task():
    LetView.delay()
    return {"status": True}

