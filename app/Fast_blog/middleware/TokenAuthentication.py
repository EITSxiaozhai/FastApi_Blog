import os
import jwt
import datetime

from fastapi import Depends, HTTPException

from app.Fast_blog.middleware.backlist import Adminoauth2_scheme

SECRET_KEY = os.getenv("SECRET_KEY")
REFRESHSECRET_KEY = os.getenv("REFSECRET_KEY")
ALGORITHM = "HS256"

def verify_token(token,typology):
    try:
        if typology == "main_token":
            # 解码 JWT，此处JWT 使用 HS256 算法进行签名
            payload = jwt.decode(token,SECRET_KEY,algorithms=["HS256"])
            # 获取过期时间（exp 字段）
            exp_timestamp = payload['exp']
            # 获取当前时间戳
            current_timestamp = datetime.datetime.utcnow().timestamp()
            detoken_username = payload['username']
            # 检查是否过期
            if current_timestamp > exp_timestamp:
                print("refresh_token 已经过期")
                return {"expired": True, "username": detoken_username}
            else:
                print("refresh_token 已经过期")
                return {"expired": True, "username": detoken_username}
        elif typology == "refresh_token":
            # 解码 JWT，此处JWT 使用 HS256 算法进行签名
            payload = jwt.decode(token,REFRESHSECRET_KEY,algorithms=["HS256"])
            # 获取过期时间（exp 字段）
            exp_timestamp = payload['exp']
            detoken_username = payload['username']
            # 获取当前时间戳
            current_timestamp = datetime.datetime.utcnow().timestamp()
            # 检查是否过期
            if current_timestamp > exp_timestamp:
                print("refresh_token 已经过期，自动签发新token")
                return {"expired": True, "username": detoken_username}
            elif current_timestamp < exp_timestamp:
                return {"expired": True, "username": detoken_username}
    except Exception as e:
        print(e)

