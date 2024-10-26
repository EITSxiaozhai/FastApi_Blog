import datetime
import os

import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from Fast_blog.middleware.backtasks import Adminoauth2_scheme

SECRET_KEY = os.getenv("SECRET_KEY")
REFRESHSECRET_KEY = os.getenv("REFSECRET_KEY")
ALGORITHM = "HS256"


class AccessTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        skip_paths = [
            "/api/user/",
            "/api/admin/user/login",
            "/api/admin/user/refreshtoken",
            "/api/views",
            "/docs",
            "/openapi.json",
            "/favicon.ico",
            "/api/generaluser",
        ]
        # Check if the request path starts with any of the skip_paths
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)
        try:
            Access_token = await Adminoauth2_scheme(request)
            detoken_username = ""
            # 将 Access_token 转换为字节类型
            Access_token_bytes = Access_token.encode('utf-8')
            payload = jwt.decode(Access_token_bytes, SECRET_KEY, algorithms=["HS256"])
            exp_timestamp = payload['exp']
            current_timestamp = datetime.datetime.utcnow().timestamp()
            detoken_username = payload['username']
            print(detoken_username)
            if current_timestamp > exp_timestamp:
                print("Access_token 已经过期。执行重新续期操作")
                return JSONResponse(status_code=401, content={"code": 50014, "message": "过期的 Access_token"})
            else:
                print("Access_token 未过期。执行后续请求")
                return await call_next(request)
        except jwt.ExpiredSignatureError:
            print("Access_token 已过期,执行重新续期操作")
            return JSONResponse(status_code=401, content={"code": 50014, "message": "无效的 Access_token"})
        except jwt.InvalidTokenError:
            print("无效的 Access_token，执行重新续期操作")
            return JSONResponse(status_code=401, content={"code": 50014, "message": "无效的 Access_token"})
        except Exception as e:
            print(f"服务器验证错误:{e}")
            return JSONResponse(status_code=500, content={"code": 50000, "message": "服务器验证错误"})
        response = await call_next(request)
        return response


async def verify_Refresh_token(Refreshtoken: str):
    try:
        detoken_username = ""
        payload = jwt.decode(Refreshtoken, REFRESHSECRET_KEY, algorithms=["HS256"])
        # 获取过期时间（exp 字段）
        exp_timestamp = payload['exp']
        # 获取当前时间戳
        current_timestamp = datetime.datetime.utcnow().timestamp()
        detoken_username = payload['username']
        # 检查是否过期
        if current_timestamp > exp_timestamp:
            print("refresh_token 已经过期。执行返回登录页面操作")
            return JSONResponse(status_code=401, content={"code": 50015, "message": "无效的refresh_token退出登录"})
        else:
            print("refresh_token 未过期")
            return {"expired": False, "username": detoken_username}
    except jwt.ExpiredSignatureError:
        print("refresh_token 已过期")
        return JSONResponse(status_code=401, content={"code": 50015, "message": "无效的refresh_token退出登录"})
