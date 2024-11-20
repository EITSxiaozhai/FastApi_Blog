# ----- coding: utf-8 ------
# author: YAO XU time:
import asyncio
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx
import jwt
import oss2
import redis
from celery import Celery
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
ADMIN_RECAPTCHA_SECRET_KEY = os.getenv("ADMIN_RECAPTCHA_SECRET_KEY")
GENERAL_USER_RECAPTCHA_SECRET_KEY = os.getenv("GENERAL_USER_RECAPTCHA_SECRET_KEY")
SMTPSERVER = os.getenv("SMTPSERVER")
SMTPPORT = os.getenv("SMTPPORT")
SMTPUSER = os.getenv("SMTPUSER")
SMTPPASSWORD = os.getenv("SMTPPASSWORD")
ALGORITHM = "HS256"

celery_app = Celery('task', broker=f'amqp://{mq_username}:{mq_password}@{mq_host}:{mq_port}/{mq_dbname}',
                    backend=f'redis://:{db_password}@{redis_host}:{redis_port}/{redis_db}')


@celery_app.task(name="update_redis_cache")
async def update_redis_cache_task():
    from Fast_blog.unit.Blog_app.BlogApi import update_redis_cache
    await update_redis_cache()
    return 0

##token缓存到redis中，暂时还没有使用
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


##Google验证码验证
async def verify_recaptcha(UserreCAPTCHA, SecretKeyTypology):
    try:
        if SecretKeyTypology == "admin":
            print("管理员验证")
            # 向Google reCAPTCHA验证端点发送POST请求来验证令牌
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://www.google.com/recaptcha/api/siteverify",
                    data={
                        "secret": ADMIN_RECAPTCHA_SECRET_KEY,
                        "response": UserreCAPTCHA,
                    },
                )
            return {"message": response.json()}
        elif SecretKeyTypology == "user":
            print("普通用户验证")
            # 向Google reCAPTCHA验证端点发送POST请求来验证令牌
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://www.google.com/recaptcha/api/siteverify",
                    data={
                        "secret": GENERAL_USER_RECAPTCHA_SECRET_KEY,
                        "response": UserreCAPTCHA,
                    },
                )
            return {"message": response.json()}
    except Exception as e:
        print(f"ERROR: {e}")
        return {"message": "服务器遇到了问题"}


###将命中率高的数据同步到redis中
class BlogCache:
    def __init__(self):
        # 创建Redis连接
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=db_password)


# 几个认证接口
Adminoauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")
Useroauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/generaluser/token")
Refresh_scheme = OAuth2PasswordBearer(tokenUrl="/api/refreshtoken")


# 阿里云操作基类
class AliOssBase:
    def __init__(self, bucket_name, upload_path, region='cn-shanghai'):
        access_key_id = os.getenv('ACCESS_KEY_ID')
        access_key_secret = os.getenv('ACCESS_KEY_SECRET')

        self.bucket_name = bucket_name
        self.upload_path = upload_path
        self.region = region  # 保存 region 值

        auth = oss2.Auth(access_key_id, access_key_secret)
        self.bucket = oss2.Bucket(auth, f'https://oss-{region}.aliyuncs.com', self.bucket_name)

    def _get_full_url(self, file_name):
        return f"https://{self.bucket_name}.oss-{self.region}.aliyuncs.com/{self.upload_path}{file_name}"

    async def async_upload(self, func, *args, **kwargs):
        await asyncio.to_thread(func, *args, **kwargs)


# 阿里云博客文章主页介绍图片
class AliOssUpload(AliOssBase):
    def __init__(self):
        super().__init__('blogcardbucket', 'blog/maincard/')

    async def upload_bitsfile(self, blogid, bitsfile):
        file_name = f'{blogid}-maincard.jpg'
        self.bucket.put_object(f'{self.upload_path}{file_name}', bitsfile)
        return self._get_full_url(file_name)

    async def upload_bitsfile_avatar(self, bitsfile):
        file_name = '-avatar.jpg'
        self.bucket.put_object(f'{self.upload_path}{file_name}', bitsfile)
        return self._get_full_url(file_name)

    def oss_upload_file(self, file_path):
        file_name = os.path.basename(file_path)
        oss_path = self.upload_path + file_name
        with open(file_path, 'rb') as file_obj:
            self.bucket.put_object(oss_path, file_obj)
        return self._get_full_url(file_name)


# 私有文档读取地址
class AliOssPrivateDocument(AliOssBase):
    def __init__(self):
        super().__init__('privatekeyjson', '/')

    def CrawlerKeyAcquisition(self):
        result = self.bucket.get_object('google.json')
        return result.read()

    def GoogleAnalytics(self):
        result = self.bucket.get_object('blog-uvpv.json')
        return result.read()


# markdown文章读取
class AliOssBlogMarkdownImg(AliOssBase):
    def __init__(self):
        super().__init__('blogmarkdownimg', 'img/', region='cn-shanghai')

    async def upload_bitsfile_markdown_img(self, bitsfile, current_blogimgconunt):
        file_name = f'{current_blogimgconunt}.jpg'
        self.bucket.put_object(f'{self.upload_path}{file_name}', bitsfile)
        return self._get_full_url(file_name)

    async def Binaryfileuploadmarkdownimg(self, bitsfile, current_blogimgconunt):
        return await self.async_upload(self.upload_bitsfile_markdown_img, bitsfile, current_blogimgconunt)
