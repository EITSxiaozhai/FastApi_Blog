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
            # 向Google reCAPTCHA验证端点发送POST请求来验证令牌
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://recaptcha.net/recaptcha/api/siteverify",
                    data={
                        "secret": ADMIN_RECAPTCHA_SECRET_KEY,
                        "response": UserreCAPTCHA,
                    },
                )
            return {"message": response.json()}
        elif SecretKeyTypology == "user":
            # 向Google reCAPTCHA验证端点发送POST请求来验证令牌
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://recaptcha.net/recaptcha/api/siteverify",
                    data={
                        "secret": GENERAL_USER_RECAPTCHA_SECRET_KEY,
                        "response": UserreCAPTCHA,
                    },
                )
            return {"message": response.json()}
    except Exception as e:
        print( f"ERROR: {e}")
        return {"message": "服务器遇到了问题"}


###将命中率高的数据同步到redis中
class BlogCache:
    def __init__(self):
        # 创建Redis连接
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=db_password)


Adminoauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")
Useroauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/generaluser/token")


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

    # 二进制上传博客首页
    def upload_bitsfile(self, blogid, bitsfile):
        self.bucket.put_object(f'{self.upload_path}{blogid}-maincard.jpg', bitsfile)

    # 二进制上传博客首页
    async def Binaryfileupload(self, blogid, bitsfile):
        await asyncio.to_thread(self.upload_bitsfile, blogid, bitsfile)
        image_url = f"http://{self.bucket_name}.oss-cn-hangzhou.aliyuncs.com/{self.upload_path}{blogid}-maincard.jpg"
        return image_url

    # 二进制上传头像
    def upload_bitsfileAvatar(self, bitsfile):
        self.bucket.put_object(f'{self.upload_path}-avatar.jpg', bitsfile)

    # 二进制上传头像
    async def Binaryfileuploadavatar(self, bitsfile):
        await asyncio.to_thread(self.upload_bitsfileAvatar, bitsfile)
        image_url = f"http://{self.bucket_name}.oss-cn-hangzhou.aliyuncs.com/{self.upload_path}-avatar.jpg"
        return image_url

    # 普通上传文件地址
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


##私有私有密钥类下载读取
class aliOssPrivateDocument():
    def __init__(self):
        access_key_id = os.getenv('ACCESS_KEY_ID')
        access_key_secret = os.getenv('ACCESS_KEY_SECRET')
        # 填写自己的 Bucket 名称和地址
        self.bucket_name = 'privatedocument'
        self.upload_path = '/'
        auth = oss2.Auth(access_key_id, access_key_secret)
        self.bucket = oss2.Bucket(auth, 'http://oss-cn-hangzhou.aliyuncs.com', self.bucket_name)

    def CrawlerKeyAcquisition(self):
        result = self.bucket.get_object('google.json')
        return result.read()


##markdown图片地址
class aliOssBlogMarkdownimg():
    def __init__(self):
        access_key_id = os.getenv('ACCESS_KEY_ID')
        access_key_secret = os.getenv('ACCESS_KEY_SECRET')

        # 填写自己的 Bucket 名称和上传地址
        self.bucket_name = 'blogmarkdown'
        self.upload_path = 'blogimg/'

        # 创建 OSS 链接
        auth = oss2.Auth(access_key_id, access_key_secret)
        self.bucket = oss2.Bucket(auth, 'http://oss-cn-shanghai.aliyuncs.com', self.bucket_name)

    def upload_bitsfileMarkdownimg(self, bitsfile, current_blogimgconunt):
        self.bucket.put_object(f'{self.upload_path}{current_blogimgconunt}.jpg', bitsfile)

        # 二进制上传博客图片

    async def Binaryfileuploadmarkdownimg(self, bitsfile, current_blogimgconunt):
        await asyncio.to_thread(self.upload_bitsfileMarkdownimg, bitsfile, current_blogimgconunt)
        image_url = f"http://{self.bucket_name}.oss-cn-shanghai.aliyuncs.com/{self.upload_path}{current_blogimgconunt}.jpg"
        return image_url
