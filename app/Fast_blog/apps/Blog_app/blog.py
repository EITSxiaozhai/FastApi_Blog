# ----- coding: utf-8 ------
# author: YAO XU time:
import dataclasses
import json
from typing import Optional
from fastapi import FastAPI, Request
from dataclasses import dataclass

from flask import jsonify
from sqlalchemy.orm import sessionmaker
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter
from uvicorn.middleware.debug import HTMLResponse
from sqlalchemy import select, text
from app.Fast_blog.database.database import engine, db_session
from app.Fast_blog.model import models
from app.Fast_blog.schemas import schemas
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
session = SessionLocal()

BlogApp = APIRouter()

templates = Jinja2Templates(directory="./Fast_blog/templates")

BlogApp.mount("/static", StaticFiles(directory="./Fast_blog/static"), name="static")


@BlogApp.get('/')
async def index(request:Request):
    async with db_session() as session:
        try:
            return templates.TemplateResponse(name="/index_page/blog_html/index.html", context={"request": request})
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
        return 0



@BlogApp.get('/about')
async def BlogAbout(request:Request):
    return templates.TemplateResponse(name="/index_page/blog_html/about.html",context={"request":request})


@BlogApp.get('/contact')
async def BlogContact(request:Request):
    return templates.TemplateResponse(name="/index_page/blog_html/contact.html",context={"request":request})




##博客添加信息
@BlogApp.post('/blogadd')
async def BlogAdd(Addtitle:str,Addcontent:str,Addauthor:str,):
    async with db_session() as session:
        try:
            x = models.Blog(title=Addtitle,content=Addcontent,author=Addauthor)
            session.add(x)
            await session.commit()
            print('文章已经添加到对应数据库')
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
        return 0

@BlogApp.get("/BlogIndex")
##博客首页API
async def BlogIndex():
    async with db_session() as session:
        try:
            stmt = select(models.Blog).order_by(models.Blog.BlogId)
            result = await session.execute(text("select * from blogtable LIMIT 3;"))
            for i in result.mappings().all():
                print(i)
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
        return 0