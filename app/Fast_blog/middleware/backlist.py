# ----- coding: utf-8 ------
# author: YAO XU time:
import asyncio
from datetime import datetime
import oss2
import os
import jwt
from celery import Celery
import redis
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer

load_dotenv()

db_password = os.getenv("REDIS_DB_PASSWORD")
redis_host = os.getenv("REDIS_DB_HOSTNAME")
redis_port = os.getenv("REDIS_DB_PORT")
redis_db = os.getenv("REDIS_DB_NAME")
redis_user = os.getenv("REDIS_USER_NAME")

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
secret_key = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

celery_app = Celery('tasks', broker=f'amqp://{mq_username}:{mq_password}@{mq_host}:{mq_port}/{mq_dbname}',
                    backend=f'redis://:{db_password}@{redis_host}:{redis_port}/{redis_db}')


@celery_app.task(name="middleware/backlist")
def add(x, y):
    return x + y


##token缓存到redis中
class TokenManager():
    def __init__(self, secret_key=secret_key):
        self.secret_key = secret_key
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, username=redis_user,
                                              password=db_password)

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


Adminoauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")
Useroauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

## 阿里云文件上传
class aliOssUpload():
    def __init__(self):
        access_key_id = os.getenv('ACCESS_KEY_ID')
        access_key_secret = os.getenv('ACCESS_KEY_SECRET')

        # 填写自己的 Bucket 名称和上传地址
        self.bucket_name = 'zpwl002'
        self.upload_path = 'blog/maincare/'

        # 创建 OSS 链接
        auth = oss2.Auth(access_key_id, access_key_secret)
        self.bucket = oss2.Bucket(auth, 'http://oss-cn-hangzhou.aliyuncs.com', self.bucket_name)

    def upload_bitsfile(self, blogid, bitsfile):
        self.bucket.put_object(f'{self.upload_path}{blogid}-maincard.jpg', bitsfile)

    async def Binaryfileupload(self, blogid, bitsfile):
        await asyncio.to_thread(self.upload_bitsfile, blogid, bitsfile)
        image_url = f"http://{self.bucket_name}.oss-cn-hangzhou.aliyuncs.com/{self.upload_path}{blogid}-maincard.jpg"
        return image_url

    def oss_upload_file(self, file_path):
        # 构造上传路径
        file_name = os.path.basename(file_path)
        oss_path = self.upload_path + file_name
        # 上传文件
        with open(file_path, 'rb') as file_obj:
            result = self.bucket.put_object(oss_path, file_obj)
        # 返回上传地址
        image_url = f"http://{self.bucket_name}.oss-cn-hangzhou.aliyuncs.com/{self.upload_path}{file_name}"
        print(image_url)
        return image_url
