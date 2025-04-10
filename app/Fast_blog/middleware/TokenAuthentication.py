import datetime
import os
from typing import Set

import jwt
from fastapi import HTTPException, status
from jwt import PyJWTError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from Fast_blog.middleware.backtasks import Adminoauth2_scheme

# 环境变量
SECRET_KEY = os.getenv("SECRET_KEY")
REFRESHSECRET_KEY = os.getenv("REFSECRET_KEY")
ALGORITHM = "HS256"

# 预定义路径集合
SKIP_PATHS: Set[str] = {
    "/api/user/",
    "/api/admin/user/login",
    "/api/admin/user/refreshtoken",
    "/api/views",
    "/docs",
    "/openapi.json",
    "/favicon.ico",
    "/api/generaluser",
    "/api/blogs/search",
    "/api/bing-wallpaper",
    "/api/bing-wallpaper/random=true",
}


# 错误响应模板
def error_response(code: int, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"code": code, "message": message}
    )


class AccessTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # 路径检查
        if any(request.url.path.startswith(path) for path in SKIP_PATHS):
            return await call_next(request)

        try:
            token = await Adminoauth2_scheme(request)
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # 验证过期时间
            if datetime.datetime.utcnow().timestamp() > payload['exp']:
                return error_response(50014, "Expired access token")

            return await call_next(request)

        except jwt.ExpiredSignatureError:
            return error_response(50014, "Expired access token")
        except PyJWTError:
            return error_response(50014, "Invalid access token")
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"code": 50000, "message": "Server authentication error"}
            )


async def validate_refresh_token(token: str) -> str:
    try:
        payload = jwt.decode(token, REFRESHSECRET_KEY, algorithms=[ALGORITHM])
        if datetime.datetime.utcnow().timestamp() > payload['exp']:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Expired refresh token"
            )
        return payload['username']
    except PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
