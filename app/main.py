import datetime
import logging
import subprocess

from fastapi import FastAPI, Response
from fastapi import FastAPI
from sqlalchemy import select
from starlette.responses import JSONResponse
from Fast_blog.database.database import engine
from sqlalchemy.orm import sessionmaker
from fastapi.staticfiles import StaticFiles
from app.Fast_blog.apps import AdminApp
from Fast_blog.apps import User_app
from Fast_blog.apps import Blog_app
from Fast_blog.apps import Power_Crawl
from Fast_blog.apps import SystemMonitoring
from fastapi.middleware.cors import CORSMiddleware
from Fast_blog.middleware.backlist import  send_activation_email
from app.Fast_blog.database.database import engine, db_session
from app.Fast_blog.model.models import Blog
from elasticsearch import Elasticsearch
from logstash_async.handler import AsynchronousLogstashHandler
import time

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

app = FastAPI()

app.include_router(User_app.UserApp, prefix='/api/generaluser', tags=["普通用户页面"])
app.include_router(Blog_app.BlogApp, prefix='/api', tags=["博客游客浏览页面"])
app.include_router(AdminApp.AdminApi, prefix='/api', tags=["超级用户管理页面"])
app.include_router(Power_Crawl.PowerApp, prefix='/api/power', tags=["电力爬虫页面"])
app.include_router(SystemMonitoring.MonitoringApp, prefix='/api/monitoring', tags=["系统监控页面"])



app.add_middleware(
    CORSMiddleware,
    ##此处URL用来允许通过的域名。提高安全性，需要根据你的进行修改
    allow_origins=["https://blog.exploit-db.xyz", "https://blogapi.exploitblog.eu.org",'http://192.168.0.149:9527','http://127.0.0.1:8000/api',"http://192.168.0.6:5173","http://192.168.0.200:5173","http://192.168.0.200:9527","http://192.168.0.6:9527","https://zpwl002.oss-cn-hangzhou.aliyuncs.com"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


celery_command = "celery -A Fast_blog.middleware.backlist worker --loglevel=info -P eventlet"
subprocess.Popen(celery_command, shell=True)

@app.get("/")
async def root():
    return {"message": "Hello world"}



@app.on_event("startup")
async def startup_event():
    pass


