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
            "request_time": record.__dict__.get("request_time", None)
        }
        return json.dumps(log_record)
