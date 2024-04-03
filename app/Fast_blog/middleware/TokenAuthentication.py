import os
import jwt
import datetime

from fastapi import Depends, HTTPException

from Fast_blog.middleware.backtasks import Adminoauth2_scheme, Refresh_scheme
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

SECRET_KEY = os.getenv("SECRET_KEY")
REFRESHSECRET_KEY = os.getenv("REFSECRET_KEY")
ALGORITHM = "HS256"


class AccessTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        #跳过用户登录接口的token验证。因为不登录无法获取token
        if request.url.path == "/api/admin/user/login":
            response = await call_next(request)
            return response
        #跳过刷新token的api。开发环境点击获取新token
        if request.url.path == "/api/admin/user/refreshtoken":
            response = await call_next(request)
            return response
        #跳过前台用户的token验证。否则用户无法查看文章
        if request.url.path.startswith("/api/views"):
            response = await call_next(request)
            return response
        #跳过开发环境中的docs文件
        if request.url.path.startswith("/docs"):
            response = await call_next(request)
            return response
        #跳过开发环境中的openapi.json文件
        if request.url.path.startswith("/openapi.json"):
            response = await call_next(request)
            return response
        if request.url.path.startswith("/favicon.ico"):
            response = await call_next(request)
            return response
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

# 函数写法。可以对单独接口添加token判断
# async def verify_Access_token(Accesstoken: str = Depends(Adminoauth2_scheme)):
#     try:
#         detoken_username = ""
#         payload = jwt.decode(Accesstoken,SECRET_KEY,algorithms=["HS256"])
#         # 获取过期时间（exp 字段）
#         exp_timestamp = payload['exp']
#         # 获取当前时间戳
#         current_timestamp = datetime.datetime.utcnow().timestamp()
#         detoken_username = payload['username']
#         print(detoken_username)
#          # 检查是否过期
#         if current_timestamp > exp_timestamp:
#             print("Access_token 已经过期。执行重新续期操作")
#             raise HTTPException(status_code=401, detail={"code": 50014, "message": "过期的 Access_token"})
#         else:
#             print("Access_token 未过期。执行后续请求")
#             return {"expired": False, "username": detoken_username}
#     except jwt.ExpiredSignatureError:
#         print("Access_token 已过期,执行重新续期操作")
#         raise HTTPException(status_code=401, detail={"code": 50014, "message": "无效的 Access_token"})
#     except jwt.InvalidTokenError:
#         print("无效的 Access_token")
#         raise HTTPException(status_code=401, detail={"code": 50014, "message": "无效的 Access_token"})

async def verify_Refresh_token(Refreshtoken:str):
    try:
        detoken_username = ""
        payload = jwt.decode(Refreshtoken,REFRESHSECRET_KEY,algorithms=["HS256"])
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
