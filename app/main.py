import logging
import multiprocessing
import os
import subprocess
from datetime import datetime
from urllib.request import Request

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from logstash_async.handler import AsynchronousLogstashHandler
from sqlalchemy.orm import sessionmaker

from Fast_blog.database.alembic_automatic import ConfigGeneration
from Fast_blog.database.databaseconnection import engine
from Fast_blog.middleware import celery_app
from Fast_blog.middleware.LogDecode import JSONLogFormatter
from Fast_blog.middleware.TokenAuthentication import AccessTokenMiddleware
from Fast_blog.unit import AdminApp, Blog_app, Power_Crawl, SystemMonitoring, User_app

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# 准备添加APM监控
app = FastAPI()
app.add_middleware(AccessTokenMiddleware)

load_dotenv()
LogStash_ip = os.getenv("LogStathIP")
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.include_router(User_app.UserApp, prefix='/api/generaluser', tags=["普通用户页面"])
app.include_router(Blog_app.BlogApp, prefix='/api/views', tags=["博客游客浏览页面"])
app.include_router(AdminApp.AdminApi, prefix='/api/admin', tags=["超级用户管理页面"])
app.include_router(Power_Crawl.PowerApp, prefix='/api/power', tags=["电力爬虫页面"])
app.include_router(SystemMonitoring.MonitoringApp, prefix='/api/monitoring', tags=["系统监控页面"])

app.add_middleware(
    CORSMiddleware,
    ##此处URL用来允许通过的域名。提高安全性，需要根据你的进行修改
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def root():
    return {"data":200}


# 设置日志通过 Logstash 发送到后端 ELK 集群上去
@app.on_event("startup")
async def startup_event():
    ConfigGeneration()
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

    # 获取真实 IP 地址
    x_real_ip = request.headers.get("x-real-ip")
    x_forwarded_for = request.headers.get("x-forwarded-for")
    client_host = x_real_ip or (x_forwarded_for.split(",")[0] if x_forwarded_for else request.client.host)

    # 解析请求信息
    request_method = request.method
    request_path = request.url.path
    status_code = response.status_code

    # 记录日志
    logger = logging.getLogger("uvicorn")

    logger.info(
        f"Request processed in {process_time}s",
        extra={
            "response_code": status_code,
            "request_method": request_method,
            "request_path": request_path,
            "request_ip": client_host,
            "request_time": process_time,
        }
    )

    return response