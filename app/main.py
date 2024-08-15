from datetime import datetime
import json
import logging
import os
import subprocess
from urllib.request import Request

from celery.app import task
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from logstash_async.handler import AsynchronousLogstashHandler
from sqlalchemy.orm import sessionmaker

from Fast_blog.database.databaseconnection import engine
from Fast_blog.middleware.TokenAuthentication import AccessTokenMiddleware
from Fast_blog.unit import AdminApp,Blog_app,Power_Crawl,SystemMonitoring,User_app
from Fast_blog.middleware.LogDecode import JSONLogFormatter
from Fast_blog.middleware.backtasks import celery_app,send_activation_email


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# 准备添加APM监控
app = FastAPI()
app.add_middleware(AccessTokenMiddleware)

load_dotenv()
LogStash_ip = os.getenv("LogStathIP")

app.include_router(User_app.UserApp, prefix='/api/generaluser', tags=["普通用户页面"])
app.include_router(Blog_app.BlogApp, prefix='/api/views', tags=["博客游客浏览页面"])
app.include_router(AdminApp.AdminApi, prefix='/api/admin', tags=["超级用户管理页面"])
app.include_router(Power_Crawl.PowerApp, prefix='/api/power', tags=["电力爬虫页面"])
app.include_router(SystemMonitoring.MonitoringApp, prefix='/api/monitoring', tags=["系统监控页面"])

app.add_middleware(
    CORSMiddleware,
    ##此处URL用来允许通过的域名。提高安全性，需要根据你的进行修改
    allow_origins=["https://blog.exploit-db.xyz","https://blogapi.exploit-db.xyz", "https://blogapi.exploitblog.eu.org", 'http://192.168.0.149:9527',
                   'http://127.0.0.1:8000','http://192.168.0.149:5173', 'http://192.168.0.149:5174','http://192.168.0.13:9527', 'http://192.168.0.13:5173','https://zpwl002.oss-cn-hangzhou.aliyuncs.com',
                   "https://static.cloudflareinsights.com"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# celery_command = "celery -A Fast_blog.middleware.backtasks worker -l info"
# # celery_beat_command = "celery -A Fast_blog.middleware.backtasks beat --loglevel=info"
# subprocess.Popen(celery_command, shell=True)
# # subprocess.Popen(celery_beat_command, shell=True)

@app.get("/")
async def root():
    return {"message": "Hello world"}

# 设置日志通过 Logstash 发送到后端 ELK 集群上去
@app.on_event("startup")
async def startup_event():
    logger = logging.getLogger("uvicorn")
    # 使用自定义的 JSON 格式化器
    formatter = JSONLogFormatter()
    logstash_handler = AsynchronousLogstashHandler(
        host=LogStash_ip,
        port=5044,
        database_path=None
    )
    logstash_handler.setFormatter(formatter)
    logger.addHandler(logstash_handler)
    logger.setLevel(logging.INFO)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds()

    # 解析请求信息
    client_host = request.client.host
    request_method = request.method
    request_path = request.url.path
    status_code = response.status_code

    # 记录日志
    logger = logging.getLogger("uvicorn")

    # 详细记录logger信息
    logger_info = (
        f"Logger Level: {logging.getLevelName(logger.level)}"
    )

    # 记录详细的logger信息和请求相关信息
    logger.info(
        f"Logger Details: {logger_info}",  # 将logger的详细信息记录到日志中
        extra={
            "response_code": status_code,
            "request_method": request_method,
            "request_path": request_path,
            "request_ip": client_host,
            "request_time": process_time
        }
    )

    return response

