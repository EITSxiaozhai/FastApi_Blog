# ----- coding: utf-8 ------
# author: YAO XU time:
import asyncio
import json
import os
from typing import Optional, Dict
from datetime import datetime, timedelta
import httpx
import jwt
import oss2
from celery import Celery
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis

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


class AsyncTokenManager:
    def __init__(self, secret_key: str, redis_client: Redis):
        """
        参数说明：
        secret_key: JWT加密密钥
        redis_client: 已初始化的异步Redis客户端
        """
        self.secret_key = secret_key
        self.redis = redis_client

    async def initialize(self):
        """可选连接验证方法"""
        await self.redis.ping()

    async def create_jwt_token(self, data: dict, expires_delta: timedelta = None) -> str:
        """生成带过期时间的JWT令牌"""
        to_encode = data.copy()
        expire_time = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire_time})
        return jwt.encode(to_encode, self.secret_key, algorithm=ALGORITHM)

    async def store_token(self, user_key: str, token: str, expiration: datetime) -> bool:
        """异步存储令牌到Redis（原子化操作）"""
        try:
            # 计算剩余秒数（包含最小存活时间保护）
            remaining = max(int((expiration - datetime.utcnow()).total_seconds()), 10)

            # 使用事务管道保证原子性
            async with self.redis.pipeline(transaction=True) as pipe:
                await pipe.setex(
                    name=f"token:{user_key}",
                    time=remaining,
                    value=token
                ).execute()
            return True
        except Exception as e:
            print(f"令牌存储失败: {str(e)}")
            return False

    async def validate_token(self, user_key: str, token: str) -> bool:
        """异步验证令牌有效性"""
        try:
            stored_token = await self.redis.get(f"token:{user_key}")

            # 双重验证机制
            return stored_token and stored_token == token and self._verify_expiration(token)
        except Exception as e:
            print(f"令牌验证异常: {str(e)}")
            return False

    def _verify_expiration(self, token: str) -> bool:
        """内部方法验证JWT有效期"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[ALGORITHM])
            return datetime.utcnow() < datetime.fromtimestamp(payload["exp"])
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
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
        self.redis_client: Redis = None

    async def initialize(self):
        """使用连接池初始化"""
        self.redis_client = Redis(
            host=os.getenv("REDIS_DB_HOSTNAME"),
            port=int(os.getenv("REDIS_DB_PORT")),
            db=int(os.getenv("REDIS_DB_NAME")),
            password=os.getenv("REDIS_DB_PASSWORD"),
            decode_responses=True,
            socket_connect_timeout=5  # 添加超时设置
        )
        # 测试连接
        await self.redis_client.ping()

    def is_ready(self):
        return self.redis_client is not None

class SessionStorage:
    def __init__(self, redis_client: Redis):  # 直接接收 Redis 客户端
        self.redis_client = redis_client
        self.memory_cache: Dict[str, dict] = {}
        self.lock = asyncio.Lock()
        self.local_ttl = 60  # 本地缓存60秒

    async def _redis_key(self, state: str) -> str:
        return f"oauth:{state}"

    async def create_session(self, state: str) -> bool:
        """创建新会话（修复参数传递）"""
        session_data = {
            "status": "pending",
            "expire_time": (datetime.now() + timedelta(minutes=5)).isoformat(),
            "user_info": None,
            "created_at": datetime.now().isoformat()
        }

        async with self.lock:
            self.memory_cache[state] = session_data

            # 正确传递参数
            asyncio.create_task(
                self._async_redis_set(
                    await self._redis_key(state),
                    json.dumps(session_data),
                    ex=300  # 现在可以正确传递关键字参数
                )
            )

        return True

    async def get_session(self, state: str) -> Optional[dict]:
        """获取会话（本地缓存优先）"""
        # 检查本地缓存
        async with self.lock:
            if state in self.memory_cache:
                session = self.memory_cache[state]
                if datetime.fromisoformat(session["expire_time"]) > datetime.now():
                    return session
                del self.memory_cache[state]

        # 从Redis获取（使用直接持有的客户端）
        redis_data = await self.redis_client.get(  # 修改这里
            await self._redis_key(state)
        )

        if redis_data:
            try:
                session = json.loads(redis_data)
                # 更新本地缓存
                async with self.lock:
                    self.memory_cache[state] = session
                return session
            except json.JSONDecodeError:
                print("Redis数据反序列化失败")
                return None
        return None

    async def update_session(self, state: str, updates: dict) -> bool:
        """原子化更新会话（修复版）"""
        lua_script = """
        local key = KEYS[1]
        local updates = cjson.decode(ARGV[1])
        local data = cjson.decode(redis.call('GET', key) or '{}')

        for k, v in pairs(updates) do
            data[k] = v
        end

        redis.call('SET', key, cjson.encode(data), 'EX', 300)
        return 1
        """

        async with self.lock:
            if state in self.memory_cache:
                self.memory_cache[state].update(updates)

            # 使用直接持有的客户端
            return bool(await self.redis_client.eval(
                lua_script,
                1,
                await self._redis_key(state),
                json.dumps(updates)
            ))

    async def _async_redis_set(self, key: str, value: str, **kwargs):
        """适配新版客户端的写入方法"""
        try:
            # 使用官方客户端的参数格式
            await self.redis_client.set(
                name=key,
                value=value,
                ex=kwargs.get('ex')  # 明确指定参数名
            )
        except Exception as e:
            print(f"Redis写入失败: {str(e)}")



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
