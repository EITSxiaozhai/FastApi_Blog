import logging
import os
import subprocess

from dotenv import load_dotenv
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from logstash_async.handler import AsynchronousLogstashHandler
from sqlalchemy.orm import sessionmaker
from Fast_blog.apps import AdminApp
from Fast_blog.apps import Blog_app
from Fast_blog.apps import Power_Crawl
from Fast_blog.apps import SystemMonitoring
from Fast_blog.apps import User_app
from Fast_blog.database.databaseconnection import engine
from Fast_blog.middleware.exception import ExceptionHandlerMiddleware

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# 准备添加APM监控
app = FastAPI()
app.add_middleware(ExceptionHandlerMiddleware)


app.include_router(User_app.UserApp, prefix='/api/generaluser', tags=["普通用户页面"])
app.include_router(Blog_app.BlogApp, prefix='/api', tags=["博客游客浏览页面"])
app.include_router(AdminApp.AdminApi, prefix='/api', tags=["超级用户管理页面"])
app.include_router(Power_Crawl.PowerApp, prefix='/api/power', tags=["电力爬虫页面"])
app.include_router(SystemMonitoring.MonitoringApp, prefix='/api/monitoring', tags=["系统监控页面"])

app.add_middleware(
    CORSMiddleware,
    ##此处URL用来允许通过的域名。提高安全性，需要根据你的进行修改
    allow_origins=["https://blog.exploit-db.xyz", "https://blogapi.exploitblog.eu.org", 'http://192.168.0.149:9527',
                   'http://127.0.0.1:8000/api', "http://192.168.0.6:5173", "http://192.168.0.200:5173",
                   "http://192.168.0.200:9527", "http://192.168.0.6:9527",
                   "https://zpwl002.oss-cn-hangzhou.aliyuncs.com"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


celery_command = "celery -A Fast_blog.middleware.backlist worker --loglevel=info -P eventlet"
subprocess.Popen(celery_command, shell=True)

@app.get("/")
async def root():
    return {"message": "Hello world"}


load_dotenv()
LogStash_ip = os.getenv("LogStathIP")
# 设置日志通过logstash去发送到后端ELK集群上去
@app.on_event("startup")
async def startup_event():
    logger = logging.getLogger("uvicorn.access")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    logger.addHandler(AsynchronousLogstashHandler(host=LogStash_ip, port=5044, database_path=None, formatter=formatter))
