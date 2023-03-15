# ----- coding: utf-8 ------
# author: YAO XU time:

from app.Fast_blog.database.database import engine
from typing import Optional
from app.Fast_blog.model import models
from sqlalchemy.orm import sessionmaker
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter
models.Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
session = SessionLocal()

BlogApp = APIRouter()

templates = Jinja2Templates(directory="./Fast_blog/templates")

BlogApp.mount("/static", StaticFiles(directory="./Fast_blog/static"), name="static")


@BlogApp.get('/')
def index(limit: int = 10, publisheds: int = None, sort: Optional[str] = None, content: Optional[str] = None):
    return {'data': f'我是博客首页，显示{limit}篇内容，并且发布状态为{publisheds}，排序顺序是根据{sort}字段'}