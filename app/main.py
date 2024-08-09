from datetime import datetime
import json
import logging
import os
import subprocess
from urllib.request import Request

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from logstash_async.handler import AsynchronousLogstashHandler
from sqlalchemy.orm import sessionmaker

from Fast_blog.database.databaseconnection import engine
from Fast_blog.middleware.TokenAuthentication import AccessTokenMiddleware
from Fast_blog.unit import AdminApp,Blog_app,Power_Crawl,SystemMonitoring,User_app
from Fast_blog.middleware.LogDecode import JSONLogFormatter

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


celery_command = "celery -A Fast_blog.middleware.backtasks worker --loglevel=info"
subprocess.Popen(celery_command, shell=True)

@app.get("/")
async def root():
    return {"message": "Hello world"}

# 设置日志通过 Logstash 发送到后端 ELK 集群上去
@app.on_event("startup")
async def startup_event():
    logger = logging.getLogger("uvicorn.access")

    # 使用自定义的 JSON 格式化器
    formatter = JSONLogFormatter()
    logstash_handler = AsynchronousLogstashHandler(
        host=LogStash_ip,
        port=5044,
        database_path=None
    )
    logstash_handler.setFormatter(formatter)
    logger.addHandler(logstash_handler)


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

    # 构建完整的日志消息
    log_message = f"{client_host} - {request_method} {request_path} {status_code} - {process_time:.2f}s"

    # 获取 uvicorn 的访问日志记录器
    logger = logging.getLogger("uvicorn.access")

    # 直接记录日志消息，不使用 extra 参数
    logger.info(log_message)

    return response

