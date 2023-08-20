# ----- coding: utf-8 ------
# author: YAO XU time:
import os
import sys
from datetime import timedelta, datetime

import jwt
from celery import Celery
import redis
from dotenv import load_dotenv


load_dotenv()


db_password = os.getenv("REDIS_DB_PASSWORD")
redis_host = os.getenv("REDIS_DB_HOSTNAME")
redis_port = os.getenv("REDIS_DB_PORT")
redis_db = os.getenv("REDIS_DB_NAME")


SECRET_KEY = "d81beb2748aa1322fe038c26dbd263907f5808548f9e428f4d9ce780dd4358a6cc942a1ee8bd49652991bce4989e270c55adeb0c5138ff516de13a07a5bdd5be"
ALGORITHM = "HS256"

celery_app = Celery('tasks',broker='amqp://admin:005q8LzBwPaVA7Mb1AY9@106.14.159.61:5672//fastapi', backend='redis://:KsicwKTvK062ichw30Av@106.14.159.61:7000/3')

#
@celery_app.task(name="middleware/backlist")
def add(x, y):
    return x + y


class TokenManager():
    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db,password=db_password)

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



