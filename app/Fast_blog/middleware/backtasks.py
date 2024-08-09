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

celery_app = Celery('tasks', broker=f'amqp://{mq_username}:{mq_password}@{mq_host}:{mq_port}/{mq_dbname}',
                    backend=f'redis://:{db_password}@{redis_host}:{redis_port}/{redis_db}')


@celery_app.task(name="middleware/backlist")
def send_activation_email(email, activation_code):
    smtp_server = SMTPSERVER
    smtp_port = 465
    smtp_user = SMTPUSER
    smtp_password = SMTPPASSWORD

    sender_email = SMTPUSER
    receiver_email = email
    subject = 'Account Activation'
    # Convert activation_code to string
    activation_code_str = str(activation_code)

    # 构建邮件内容
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    body = f'Your activation code is: {activation_code_str}'
    msg.attach(MIMEText(body, 'plain'))

    # 连接到 SMTP 服务器并发送邮件
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(smtp_user, smtp_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())


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


Adminoauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")
Useroauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/generaluser/token")
Refresh_scheme = OAuth2PasswordBearer(tokenUrl="/api/refreshtoken")

# 定义一个基类，用于与阿里云OSS进行基本的交互
class AliOssBase:
    def __init__(self, bucket_name, endpoint, upload_path):
        access_key_id = os.getenv('ACCESS_KEY_ID')  # 从环境变量获取Access Key ID
        access_key_secret = os.getenv('ACCESS_KEY_SECRET')  # 从环境变量获取Access Key Secret
        auth = oss2.Auth(access_key_id, access_key_secret)  # 创建OSS认证对象
        self.bucket = oss2.Bucket(auth, endpoint, bucket_name)  # 创建Bucket对象
        self.upload_path = upload_path  # 设置上传路径


    # 上传文件到OSS
    def upload_file(self, oss_path, file_obj):
        try:
            self.bucket.put_object(oss_path, file_obj)  # 将文件上传到OSS
            return f"http://oss-cn-hangzhou.aliyuncs.com/{oss_path}"   # 返回文件的URL
        except oss2.exceptions.OssError as e:  # 处理上传过程中可能出现的异常
            print(f"文件上传到OSS失败: {e}")  # 打印错误信息
            return None  # 返回None表示上传失败

    # 异步上传文件到OSS
    async def async_upload_file(self, oss_path, file_obj):
        return await asyncio.to_thread(self.upload_file, oss_path, file_obj)  # 使用线程池执行同步的上传操作


# 定义一个子类，用于特定的上传操作
class AliOssUpload(AliOssBase):
    def __init__(self):
        super().__init__('zpwl002', 'http://oss-cn-hangzhou.aliyuncs.com/', 'blog/maincare/')  # 初始化基类

    # 上传博客主卡图片
    def upload_bitsfile(self, blogid, bitsfile):
        return self.upload_file(f'{self.upload_path}{blogid}-maincard.jpg', bitsfile)  # 调用基类的方法上传文件

    # 异步上传博客主卡图片
    async def async_upload_bitsfile(self, blogid, bitsfile):
        return await self.async_upload_file(f'{self.upload_path}{blogid}-maincard.jpg', bitsfile)  # 调用基类的异步方法上传文件

    # 上传头像图片
    def upload_avatar(self, bitsfile):
        return self.upload_file(f'{self.upload_path}-avatar.jpg', bitsfile)  # 调用基类的方法上传文件

    # 异步上传头像图片
    async def async_upload_avatar(self, bitsfile):
        return await self.async_upload_file(f'{self.upload_path}-avatar.jpg', bitsfile)  # 调用基类的异步方法上传文件

    # 上传本地文件
    def upload_local_file(self, file_path):
        file_name = os.path.basename(file_path)  # 获取文件名
        with open(file_path, 'rb') as file_obj:  # 以二进制模式打开文件
            return self.upload_file(f'{self.upload_path}{file_name}', file_obj)  # 调用基类的方法上传文件


# 定义一个子类，用于处理私有文档的操作
class AliOssPrivateDocument(AliOssBase):
    def __init__(self):
        super().__init__('privatedocument', 'http://oss-cn-hangzhou.aliyuncs.com', '/')  # 初始化基类

    # 获取爬虫密钥
    def get_crawler_key(self):
        try:
            result = self.bucket.get_object('google.json')  # 从OSS获取对象
            return result.read()  # 读取对象内容
        except oss2.exceptions.OssError as e:  # 处理获取过程中可能出现的异常
            print(f"从OSS获取对象失败: {e}")  # 打印错误信息
            return None  # 返回None表示获取失败


# 定义一个子类，用于上传Markdown博客图片
class AliOssBlogMarkdownImg(AliOssBase):
    def __init__(self):
        super().__init__('blogmarkdown', 'http://oss-cn-shanghai.aliyuncs.com/', 'blogimg/')  # 初始化基类

    # 上传博客图片
    def upload_blog_image(self, bitsfile, image_count):
        return self.upload_file(f'{self.upload_path}{image_count}.jpg', bitsfile)  # 调用基类的方法上传文件

    # 异步上传博客图片
    async def async_upload_blog_image(self, bitsfile, image_count):
        return await self.async_upload_file(f'{self.upload_path}{image_count}.jpg', bitsfile)  # 调用基类的异步方法上传文件