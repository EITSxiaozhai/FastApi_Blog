import json
import logging
import os

from dotenv import load_dotenv

load_dotenv()
LogStash_ip = os.getenv("LogStathIP")


class JSONLogFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "message": record.getMessage(),
            "logger_name": record.name,
            "func_name": record.funcName,
            "file_name": record.pathname,
            "response_code": record.__dict__.get("response_code", None),
            "request_method": record.__dict__.get("request_method", None),
            "request_path": record.__dict__.get("request_path", None),
            "request_ip": record.__dict__.get("request_ip", None),
            "request_time": record.__dict__.get("request_time", None),
            # 新增的时间统计字段
            "request_time_seconds": record.__dict__.get("request_time_seconds", None),
            "request_time_ms": record.__dict__.get("request_time_ms", None),
            "request_time_formatted": record.__dict__.get("request_time_formatted", None),
            "user_agent": record.__dict__.get("user_agent", None),
            "request_size": record.__dict__.get("request_size", None),
            "start_time": record.__dict__.get("start_time", None),
            "end_time": record.__dict__.get("end_time", None),
            "is_slow_request": record.__dict__.get("is_slow_request", False),
            "performance_category": record.__dict__.get("performance_category", None),
            "duration_category": record.__dict__.get("duration_category", None)
        }
        return json.dumps(log_record)
