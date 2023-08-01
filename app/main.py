import asyncio

import anyio
from celery import Celery
from celery.result import AsyncResult
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
from app.Fast_blog.database.database import engine
from Fast_blog.apps import User_app
from Fast_blog.apps import Blog_app
from Fast_blog.apps import Power_Crawl
from Fast_blog.apps.Power_Crawl import LetView
from fastapi.middleware.cors import CORSMiddleware
from Fast_blog.BackList.backlist import add,celery_app


SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
session = SessionLocal()



app = FastAPI()


app.include_router(User_app.UserApp,prefix='/user', tags=["用户"])
app.include_router(Blog_app.BlogApp,prefix='/api',tags=["博客"])
app.include_router(Power_Crawl.PowerApp,prefix='/power', tags=["电力爬虫"])



templates = Jinja2Templates(directory="./Fast_blog/templates")

app.mount("/static", StaticFiles(directory="./Fast_blog/static"), name="static")



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





@app.get("/")
async def root():
     response_data = {"message": "hahahah"}
     add.delay(12,12)
     return JSONResponse(content=response_data)


