# ----- coding: utf-8 ------
# author: YAO XU time:
import json
import os
import pickle
import sys
from datetime import timedelta, datetime

import jwt
from celery import Celery
import redis
from dotenv import load_dotenv
from sqlalchemy import select,event
from app.Fast_blog.database.database import db_session
from app.Fast_blog.model.models import Blog
load_dotenv()

db_password = os.getenv("REDIS_DB_PASSWORD")
redis_host = os.getenv("REDIS_DB_HOSTNAME")
redis_port = os.getenv("REDIS_DB_PORT")
redis_db = os.getenv("REDIS_DB_NAME")

mq_password = os.getenv("MQ_USERPASSWORD")
mq_username = os.getenv("MQ_USERNAME")
mq_host = os.getenv("MQ_HOSTNAME")
mq_dbname = os.getenv("MQ_DBNAME")
mq_port = os.getenv("MQ_DBPORT")


db_username = os.getenv("DB_USERNAME")
mysqldb_password = os.getenv("DB_PASSWORD")
db_hostname = os.getenv("DB_HOSTNAME")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

ALGORITHM = "HS256"

celery_app = Celery('tasks', broker=f"'amqp://{mq_username}:{mq_password}@{mq_host}:{mq_port}//{mq_dbname}'",
                    backend=f"'redis://:{db_password}@{redis_host}:{redis_port}/{redis_db}'")



@celery_app.task(name="middleware/backlist")
def add(x, y):
    return x + y



##token缓存到redis中
class TokenManager():
    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=db_password)

    def create_jwt_token(self, data: dict) -> str:
        token = jwt.encode(data, self.secret_key, algorithm=ALGORITHM)
        return token

    def store_token_in_redis(self, username: str, token: str, expiration: datetime):
        remaining_seconds = max((expiration - datetime.now()).total_seconds(), 100)
        # 将剩余过期时间转换为整数
        remaining_seconds = int(remaining_seconds)
        self.redis_client.setex(username, remaining_seconds, token)

    def validate_token(self, username: str, token: str) -> bool:
        stored_token = self.redis_client.get(username)

        if stored_token and stored_token.decode("utf-8") == token:
            return True

        return False


###将命中率高的数据同步到redis中
class BlogCache:
    def __init__(self):
        # 创建Redis连接
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=db_password)



