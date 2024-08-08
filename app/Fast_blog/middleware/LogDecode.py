from datetime import datetime
import json
import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from logstash_async.handler import AsynchronousLogstashHandler
from urllib.request import Request

load_dotenv()
LogStash_ip = os.getenv("LogStathIP")
app = FastAPI()

class JSONLogFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger_name": record.name,
            "func_name": record.funcName,
            "file_name": record.pathname,
            "line_no": record.lineno,
            "response_code": record.__dict__.get("response_code", None),
            "request_method": record.__dict__.get("request_method", None),
            "request_path": record.__dict__.get("request_path", None),
            "request_ip": record.__dict__.get("request_ip", None),
            "request_time": record.__dict__.get("request_time", None)
        }
        return json.dumps(log_record)

# 设置日志通过 Logstash 发送到后端 ELK 集群上去
@app.on_event("startup")
async def startup_event():
    logger = logging.getLogger("uvicorn.access")
    logger.setLevel(logging.INFO)

    # 使用自定义的 JSON 格式化器
    formatter = JSONLogFormatter()
    logstash_handler = AsynchronousLogstashHandler(
        host=LogStash_ip,
        port=5044,
        database_path=None
    )
    logstash_handler.setFormatter(formatter)
    logger.addHandler(logstash_handler)

# 创建中间件来记录请求和响应的信息
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds()

    # 解析请求信息
    client_host = request.client.host
    request_method = request.method
    request_path = request.url.path

    log_data = {
        "response_code": response.status_code,
        "request_method": request_method,
        "request_path": request_path,
        "request_ip": client_host,
        "request_time": process_time
    }
    logger = logging.getLogger("uvicorn.access")
    logger.info(
        f"{client_host} - {request_method} {request_path} {response.status_code}",
        extra=log_data
    )
    return response