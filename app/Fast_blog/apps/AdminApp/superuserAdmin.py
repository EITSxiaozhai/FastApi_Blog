import json
import os
import uuid
import datetime

from fastapi import HTTPException, FastAPI

import jwt
from fastapi import APIRouter, Request, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy import select, update, delete
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload
from starlette.background import BackgroundTasks
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
from app.Fast_blog.database.database import db_session
from app.Fast_blog.middleware.backlist import Adminoauth2_scheme,aliOssPrivateDocument,aliOssUpload, verify_recaptcha
from app.Fast_blog.model import models
from app.Fast_blog.model.models import AdminUser, UserPrivileges, Blog, BlogTag, ReptileInclusion
from app.Fast_blog.schemas.schemas import UserCredentials
AdminApi = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_jwt_token(data: dict) -> str:
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token


async def verify_password(username: str, password: str) -> bool:
    async with db_session() as session:
        getusername = username
        getpassword = password
        results = await session.execute(select(AdminUser).filter(AdminUser.username == getusername))
        user = results.scalar_one_or_none()
        if user is None:
            # 用户名不存在
            raise HTTPException(status_code=401, detail="验证未通过")
        elif user.userpassword != getpassword:
            # 密码不匹配
            raise HTTPException(status_code=401, detail="验证未通过")
        else:
            return True
    # 在这里进行密码验证的逻辑，比如查询数据库，验证用户名和密码是否匹配
    # 返回 True 或 False
    # ...
    return True  # 示例中直接返回 True，您需要根据实际情况进行验证


@AdminApi.post("/token")
async def Token(Incoming: OAuth2PasswordRequestForm = Depends()):
    async with db_session() as session:
        getusername = Incoming.username
        getpassword = Incoming.password
        if not await verify_password(getusername, getpassword):
            raise HTTPException(status_code=401, detail="验证未通过")
        # print(getusername)
        # results = await session.execute(select(AdminUser).filter(AdminUser.username == getusername))
        # user = results.scalar_one_or_none()
        # if user is None:
        #     # 用户名不存在
        #     raise HTTPException(status_code=401, detail="验证未通过")
        # elif user.userpassword != getpassword:
        #     # 密码不匹配
        #     raise HTTPException(status_code=401, detail="验证未通过")
        # else:
        token_data = {
            "username": Incoming.username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        token = create_jwt_token(data=token_data)
        return {"access_token": token, "token_type": 'Bearer', "token": token}


# "https://recaptcha.net/recaptcha/api/siteverify",
# {
#   params: {
#     secret: "6LdFp74UXXXXXXXXXXXXXXXXXXXXXX-XXXXXXXXXXXXXXXXX",
#     response: ctx.query.token
# }



# async def verify_recaptcha(UserreCAPTCHA):
#     # 向Google reCAPTCHA验证端点发送POST请求来验证令牌
#     async with httpx.AsyncClient() as client:
#         response = await client.post(
#             "https://recaptcha.net/recaptcha/api/siteverify",
#             data={
#                 "secret": RECAPTCHA_SECRET_KEY,
#                 "response": UserreCAPTCHA,
#             },
#         )
#
#     # 检查验证响应
#     if response.status_code != 200:
#         raise HTTPException(status_code=500, detail="reCAPTCHA验证失败")
#
#     # 解析验证响应
#     verification_result = response.json()
#
#     # 检查reCAPTCHA验证是否成功
#     if not verification_result.get("success"):
#         raise HTTPException(status_code=400, detail="reCAPTCHA验证失败")
#
#     return {"message": response.json()}


@AdminApi.post("/user/login")
##博客登录
async def UserLogin(x: UserCredentials, request: Request):
    try:
        RecaptchaResponse = await verify_recaptcha(UserreCAPTCHA=x.googlerecaptcha,SecretKeyTypology="admin")
        print(RecaptchaResponse)
        if RecaptchaResponse["message"]["success"]:
            token_data = await Token(OAuth2PasswordRequestForm(
                username=x.username,
                password=x.password,
            ))
            if "token" in token_data:
                return {
                    "code": 20000,
                    "data": {
                        "token": token_data["token"],
                        "msg": "登录成功",
                        "state": "true"
                    }
                }
        else:
            return {"code": 40001, "message": "登录失败。"}
    # 如果用户未经过身份验证或凭据无效
    except jwt.ExpiredSignatureError:
        return {"code": 40002, "message": "Token已过期"}
    except jwt.InvalidTokenError:
        return {"code": 40003, "message": "无效的Token"}


@AdminApi.get("/user/info")
async def Userinfo(request: Request, token: str = Depends(Adminoauth2_scheme)):
    async with db_session() as session:
        try:
            print(token)
            if token:
                token = token.replace("Bearer", "").strip()
                # Verify and decode the token
                token_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                username = token_data.get("username")
                if username:
                    stmt = select(models.AdminUser).join(models.UserPrivileges).add_columns(
                        models.UserPrivileges.privilegeName).filter(
                        models.AdminUser.username == username
                    )
                    result = await db_session.execute(stmt)
                    user, privileges = result.fetchone()

                    if user:
                        return {"code": 20000, "data":
                            {
                                "roles": [f"{privileges}"],
                            }
                                }
            return {"code": 20001, "message": "用户未找到"}
        except jwt.ExpiredSignatureError:
            return {"code": 40002, "message": "Token已过期"}
        except jwt.InvalidTokenError:
            return {"code": 40003, "message": "无效的Token"}
        except Exception as e:
            print("博客Admin token 转移我们遇到了下面的问题")
            print(e)
            return {"code": 50000, "message": "内部服务器错误"}


@AdminApi.get("/transaction/list")
##博客Admin 动态权限生成菜单
async def Userinfo(token: str = Depends(Adminoauth2_scheme)):
    async with db_session() as session:
        try:
            # Get the token from the request headers
            if token:
                # Verify and decode the token
                token_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

                username = token_data.get("username")
                if username:
                    stmt = select(models.AdminUser).join(models.UserPrivileges).add_columns(
                        models.UserPrivileges.privilegeName).filter(
                        models.AdminUser.username == username
                    )
                    result = await db_session.execute(stmt)
                    user, privileges = result.fetchone()
                    if user:
                        return {"code": 20000, "data":
                            {
                                "roles": [f"{privileges}"],
                            }
                                }
            return {"code": 20001, "message": "用户未找到"}
        except jwt.ExpiredSignatureError:
            return {"code": 40002, "message": "Token已过期"}
        except jwt.InvalidTokenError:
            return {"code": 40003, "message": "无效的Token"}
        except Exception as e:
            print("动态菜单鉴权我们遇到了下面的问题")
            print(e)
            return {"code": 50000, "message": "内部服务器错误"}


@AdminApi.post("/user/adminlist")
async def AllAdminUser(token: str = Depends(Adminoauth2_scheme)):
    async with db_session() as session:
        try:
            if token:
                sql = select(AdminUser)
                result = await session.execute(sql)
                data = result.scalars().all()

                modified_data = []
                for item in data:
                    user_privilege = await session.scalar(
                        select(UserPrivileges.privilegeName)
                        .where(UserPrivileges.NameId == item.userPrivileges)
                    )
                    if user_privilege is not None:
                        item_dict = item.to_dict()
                        item_dict["privilegeName"] = user_privilege
                        modified_data.append(item_dict)
                return {"code": 20000, "data": modified_data}
        except jwt.ExpiredSignatureError:
            return {"code": 40002, "message": "Token已过期"}
        except jwt.InvalidTokenError:
            return {"code": 40003, "message": "无效的Token"}
        except Exception as e:
            return {"code": 50000, "message": "内部服务器错误"}


def UUID_crt(UuidApi):
    UuidGenerator = uuid.uuid5(uuid.NAMESPACE_DNS, UuidApi)
    return UuidGenerator


async def GetUser(inputusername: str, token: str = Depends(Adminoauth2_scheme)):
    async with db_session() as session:
        try:
            stmt = select(models.AdminUser).filter_by(username=inputusername)
            result = await session.execute(stmt)
            for row in result.scalars():
                x = row.__dict__['username']
                return ({"Username:": x})
        except Exception as e:
            print(e)


@AdminApi.get("/Adminadd")
async def query(inputname: str, inpassword: str, inEmail: EmailStr, ingender: bool, Typeofuser: bool,
                token: str = Depends(Adminoauth2_scheme)):
    async with db_session() as session:
        try:
            UserQurey = await GetUser(inputusername=inputname)
            if UserQurey != None:
                return ({"用户已经存在,存在值为:": UserQurey['username']})
            elif UserQurey == None:
                x = models.AdminUser(username=inputname, userpassword=inpassword, UserEmail=inEmail, gender=ingender,
                                     userPrivileges=Typeofuser, UserUuid=str((UUID_crt(inputname))))
                session.add(x)
                await session.commit()
                print("用户添加成功")
                return ({"用户添加成功,你的用户名为:": inputname})
        except Exception as e:
            print(e)
        return {"重复用户名": UserQurey}


@AdminApi.post("/user/updateUser")
async def UpdateUser(request: Request, token: str = Depends(Adminoauth2_scheme)):
    async with db_session() as session:
        try:
            data = await request.json()  # This will extract the JSON data from the request body
            print(data)
            stmt = select(models.AdminUser).filter_by(
                username=data["username"])  # Assuming "username" is the primary key
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                # Update the user's information based on the received data
                user.UserEmail = data["UserEmail"]
                user.UserUuid = data["UserUuid"]
                user.gender = data["gender"]["code"]

                # Map privilege name to privilege value using Typeofuserchoices
                privilege_name = data["userprivilegesData"]
                privilege_value = None
                for choice in models.UserPrivileges.Typeofuserchoices:
                    if choice[1] == privilege_name:
                        privilege_value = choice[0]
                        break

                if privilege_value is not None:
                    # Query the privilege value by privilege_name
                    privilege = await session.execute(
                        select(models.UserPrivileges).where(models.UserPrivileges.privilegeName == privilege_name))
                    privilege = privilege.scalar_one_or_none()
                    if privilege:
                        user.userPrivileges = privilege.NameId

                await session.commit()
                return {"code": 20000}
            else:
                return {"data": "User not found"}
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
            return {"code": 50000}  # Return an appropriate error code


@AdminApi.post("/user/getTypeofuserData")
##博客Admin权限管理
async def UserPrivilegeName(request: Request, token: str = Depends(Adminoauth2_scheme)):
    async with db_session() as session:
        try:
            data = await request.json()
            stmt = select(models.AdminUser).filter_by(
                usename=data['username'])  # Assuming "username" is the primary key
            stmt = stmt.options(joinedload(AdminUser.userPrivileges))
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            if user:
                privilege = user.userPrivileges.privilegeName
                return {"code": 20000, "privilegeName": privilege}
            else:
                return {"code": 20001, "message": "User not found"}
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
        return {"code": 20001, "message": "User not found"}


@AdminApi.post("/user/userprivileges")
async def get_user_privileges():
    async with db_session() as session:
        try:
            # 查询所有不同的权限值
            privileges = await session.execute(
                select(UserPrivileges.privilegeName).distinct()
            )
            privilege_values = [privilege.code for privilege in privileges.scalars()]
            return {"code": 20000, "data": privilege_values}
        except NoResultFound:
            return []


@AdminApi.get("/user/logout")
##博客Admin退出系统
async def UserloginOut():
    async with db_session() as session:
        try:
            return {"data": "success"}
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
        return 0


## Admin页面博客添加
@AdminApi.post('/blogadd')
async def BlogAdd(Addtitle: str, Addcontent: str, Addauthor: str, file_path: str, background_tasks: BackgroundTasks,
                  request: Request, token: str = Depends(Adminoauth2_scheme)):
    async with db_session() as session:
        try:
            # 将文件保存到磁盘
            # file_path = os.path.join(static_folder_path, "uploadimages", file.filename)
            # with open(file_path, "wb") as f:
            #     shutil.copyfileobj(file.file, f)
            content_binary = Addcontent.encode("utf-8")
            image_url = aliOssUpload().oss_upload_file(file_path)

            # base_url = str(request.base_url)
            # 构建完整的URL地址
            # image_url = f"{base_url.rstrip('/')}/static/uploadimages/{file.filename}"
            # 构建参数值字典
            new_blog_entry = Blog(
                title=Addtitle,
                content=content_binary,
                BlogIntroductionPicture=image_url,
                author=Addauthor,
                created_at=datetime.datetime.now(),
            )
            session.add(new_blog_entry)
            await session.commit()
            return {'message': '文章已经添加到对应数据库', 'image_url': image_url}

        except Exception as e:
            print("我们遇到了下面的问题", {"data": e})


@AdminApi.post('/Blogtaglist')
async def BlogTagList(token: str = Depends(Adminoauth2_scheme)):
    async with db_session() as session:
        try:
            sql = select(models.BlogTag)
            result = await session.execute(sql)  # 使用 execute_async 替代 execute
            enddata = {}
            for tag in result.scalars().all():
                if tag.blog_id not in enddata:
                    sql2 = select(models.Blog).filter_by(BlogId=tag.blog_id)
                    blogresult = await session.execute(sql2)
                    for blogname in blogresult.scalars().all():
                        enddata[tag.blog_id] = {
                            'TagName': tag.Article_Type,
                            'Date': blogname.created_at,
                            'Title': blogname.title,
                        }
            return {"data": enddata, "code": 20000}
        except Exception as e:
            print("我们遇到了下面的问题", e)


@AdminApi.post('/Blogtagcreate/{blog_id}/{type}')
async def BlogTagcreate(type: str, blog_id: int, token: str = Depends(Adminoauth2_scheme)):
    async with db_session() as session:
        try:
            new_type = models.BlogTag(Article_Type=type, blog_id=blog_id)
            session.add(new_type)
            await session.commit()
            return {"data": new_type, "code": 20000}
        except Exception as e:
            print("我们遇到了下面的问题", {"data": e})


@AdminApi.post('/Blogtagmodify/{blog_id}/{type}')
async def BlogTagModify(blog_id: int, type: str, token: str = Depends(Adminoauth2_scheme)):
    async with db_session() as session:
        try:
            # 查询是否存在对应的记录
            sql_select = select(models.Blog).filter_by(BlogId=blog_id)
            result_select = await session.execute(sql_select)

            if len(result_select.all()) == 0:
                return {"data": "没有查到对应的ID跳过修改", "code": 50000}

            # 查询并修改指定的记录
            sql_update = update(models.BlogTag).where(
                (models.BlogTag.blog_id == blog_id) & (models.BlogTag.Article_Type == type)
            ).values(tag_created_at=datetime.datetime.now())

            # 使用 fetchall 获取所有结果
            result_update = await session.execute(sql_update)
            await session.flush()

            return {"data": "修改成功", "code": 20000}
        except Exception as e:
            print("我们遇到了下面的问题", {"data": str(e)})



# SCOPES = ['https://www.googleapis.com/auth/indexing']
# ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
# JSON_KEY_FILE = "C:\\Users\\admin\\Desktop\\google.json"

aliOssPrivateDocument = aliOssPrivateDocument()


@AdminApi.get('/blogseo/googleoauth2')
async def url_sent(background_tasks: BackgroundTasks,token: str = Depends(Adminoauth2_scheme)):
    try:
        background_tasks.add_task(publish_url_notification)
        return {"data": "请求已经发送", "code": 20000}
    except Exception as e:
        print("我们遇到了下面的问题", {"data": str(e)})

async def publish_url_notification(notification_type="URL_UPDATED"):
    async with db_session() as session:
        try:
            # 异步执行查询
            all_blog_ids = await session.execute(select(Blog.BlogId))

            for blog_id in all_blog_ids.scalars():
                # 构建博客的完整URL
                blog_url = f"https://blog.exploit-db.xyz/blog/{blog_id}"

                # 发送通知
                JSON_KEY_FILE = aliOssPrivateDocument.CrawlerKeyAcquisition()
                JSON_KEY_FILE_str = JSON_KEY_FILE.decode('utf-8')
                JSON_KEY_FILE = json.loads(JSON_KEY_FILE_str.replace("'",'"').replace('\r\n', '\\r\\n'), strict=False)
                SCOPES = ['https://www.googleapis.com/auth/indexing']
                ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
                print(SCOPES)
                credentials = ServiceAccountCredentials.from_json_keyfile_dict(JSON_KEY_FILE,scopes=SCOPES)
                http = credentials.authorize(httplib2.Http())
                content = {
                    "url": blog_url,
                    "type": "URL_UPDATED"
                }
                response, response_content = http.request(ENDPOINT, method="POST", body=str(content))
                get_info = http.request(f"https://indexing.googleapis.com/v3/urlNotifications/metadata?url={blog_url}",
                                        method="GET")

                # 更新或创建 ReptileInclusion 表的相应记录
                status = response.get('status', '')

                # 异步执行查询

                reptile_inclusion_query = await session.execute(
                    select(ReptileInclusion).filter(ReptileInclusion.blog_id == blog_id))

                reptile_inclusion = reptile_inclusion_query.scalar()

                if reptile_inclusion is not None:
                    existing_reptile_inclusion = reptile_inclusion

                    # 创建一个新的 ReptileInclusion 对象，将其标识符设置为与现有对象相同
                    updated_reptile_inclusion = ReptileInclusion(
                        blog_id=existing_reptile_inclusion.blog_id,
                        GoogleSubmissionStatus=status,
                        Submissiontime=datetime.datetime.now(),
                        ReturnLog=response
                    )

                    # 使用当前会话将新对象添加到数据库
                    session.add(updated_reptile_inclusion)
                else:
                    # 记录不存在，创建新的记录
                    new_reptile_inclusion = ReptileInclusion(blog_id=blog_id,
                                                             GoogleSubmissionStatus=status,
                                                             Submissiontime=datetime.datetime.now(),
                                                             ReturnLog=response)
                    session.add(new_reptile_inclusion)

                # 提交异步事务
                await session.commit()

        except Exception as e:
            print("发生错误:", e)



