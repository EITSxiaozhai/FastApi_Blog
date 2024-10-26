import datetime
import json
import os
import uuid

import httplib2
import jwt
import requests
from fastapi import APIRouter, Request, Depends, File
from fastapi import HTTPException, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from oauth2client.service_account import ServiceAccountCredentials
from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.orm import joinedload
from starlette.background import BackgroundTasks
from starlette.responses import JSONResponse

from Fast_blog.database.databaseconnection import db_session
from Fast_blog.middleware import verify_Refresh_token
from Fast_blog.middleware.backtasks import Adminoauth2_scheme, verify_recaptcha, \
    AliOssBlogMarkdownImg, AliOssPrivateDocument
from Fast_blog.model import models
from Fast_blog.model.models import AdminUser, UserPrivileges, Blog, ReptileInclusion, BlogTag
from Fast_blog.schemas.schemas import AdminUserModel
from Fast_blog.schemas.schemas import BlogCreate, BlogTagModel
from Fast_blog.schemas.schemas import UserCredentials
from Fast_blog.unit.Blog_app.BlogApi import uploadoss

AdminApi = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
REFRESHSECRET_KEY = os.getenv("REFSECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# 根据不同了类型调用不同的加密密钥
def create_jwt_token(data: dict, typology) -> str:
    if typology == "main_token":
        token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
        return token
    elif typology == "refresh_token":
        token = jwt.encode(data, REFRESHSECRET_KEY, algorithm=ALGORITHM)
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


@AdminApi.post("/token")
async def Token(Incoming: OAuth2PasswordRequestForm = Depends()):
    async with db_session() as session:
        getusername = Incoming.username
        getpassword = Incoming.password
        if not await verify_password(getusername, getpassword):
            raise HTTPException(status_code=401, detail="验证未通过")
        token_data = {
            "username": Incoming.username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=40)
        }
        token = create_jwt_token(data=token_data, typology="main_token")
        Retoken_data = {
            "username": Incoming.username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        Retoken = create_jwt_token(data=Retoken_data, typology="refresh_token")
        return {"access_token": token, "token_type": 'Bearer', "token": token, "refresh_token": Retoken}


@AdminApi.post("/user/login")
# 博客登录
async def UserLogin(x: UserCredentials, request: Request):
    try:
        RecaptchaResponse = await verify_recaptcha(UserreCAPTCHA=x.googlerecaptcha, SecretKeyTypology="admin")
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
                        "refresh_token": token_data["refresh_token"],
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


@AdminApi.post("/user/refreshtoken")
async def Refreshtoken(request: Request):
    # 获取请求头中的 Authorization 值
    authorization_header = request.headers.get('authorization')
    # 检查是否存在 Authorization 头
    if authorization_header:
        # 使用空格分割字符串，并获取第二部分（即令牌内容）
        token = authorization_header.split('Bearer ')[1]
        Refreshtoken_verification = await verify_Refresh_token(Refreshtoken=token)
        print(Refreshtoken_verification)
        if Refreshtoken_verification["expired"] == False and Refreshtoken_verification["username"] != "":
            token = create_jwt_token(data={"username": Refreshtoken_verification["username"],
                                           "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=40)},
                                     typology="main_token")
            refresh_token = create_jwt_token(data={"username": Refreshtoken_verification["username"],
                                                   "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60)},
                                             typology="refresh_token")
            return \
                {
                    "code": 20000,
                    "data":
                        {
                            "token": token,
                            "refresh_token": refresh_token,
                            "message": "token刷新成功",
                            "code": 20000,
                        }
                }
        else:
            return JSONResponse(status_code=401, content={"code": 50015, "message": "无效的refresh_token退出登录"})
    else:
        print("Authorization Header not found.")
        return JSONResponse(status_code=401, content={"code": 50015, "message": "无效的refresh_token退出登录"})


@AdminApi.get("/user/info")
async def Userinfo(request: Request, token: str = Depends(Adminoauth2_scheme)):
    async with db_session() as session:
        try:
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
            return {"code": 50012, "message": "Token已过期", "error": "Token已经过期"}
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
            return {"code": 50012, "message": "Token已过期", "error": "Token已经过期"}
        except jwt.InvalidTokenError:
            return {"code": 40003, "message": "无效的Token"}
        except Exception as e:
            print("动态菜单鉴权我们遇到了下面的问题")
            print(e)
            return {"code": 50000, "message": "内部服务器错误"}


@AdminApi.post("/user/adminlist")
async def AllAdminUser():
    async with db_session() as session:
        try:
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
            return {"code": 50012, "message": "Token已过期", "error": "Token已经过期"}
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


@AdminApi.post("/user/Adminadd")
async def AdminUserAdd(inputuser: AdminUserModel):
    async with db_session() as session:
        try:
            UserQurey = await GetUser(inputusername=inputuser.username)
            if UserQurey != None:
                return ({"用户已经存在,存在值为:": UserQurey['username']})
            elif UserQurey == None:
                x = models.AdminUser(username=inputuser.username, userpassword=inputuser.userpassword,
                                     UserEmail=inputuser.UserEmail, gender=inputuser.gender,
                                     userPrivileges=inputuser.userprivilegesData,
                                     UserUuid=str((UUID_crt(inputuser.username))))
                session.add(x)
                await session.commit()
                print("用户添加成功")
                return ({"用户添加成功,你的用户名为:": inputuser.username})
        except jwt.ExpiredSignatureError:
            return {"code": 50012, "message": "Token已过期", "error": "Token已经过期"}
        except jwt.InvalidTokenError:
            return {"code": 40003, "message": "无效的Token"}
        except Exception as e:
            print(e)
            return {"code": 50000, "message": "内部服务器错误"}
        return {"重复用户名": UserQurey}


@AdminApi.post("/user/updateUser")
async def UpdateUser(request: Request, ):
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
        except jwt.ExpiredSignatureError:
            return {"code": 50012, "message": "Token已过期"}
        except jwt.InvalidTokenError:
            return {"code": 40003, "message": "无效的Token"}
        except Exception as e:
            return {"code": 50000, "message": "内部服务器错误"}


@AdminApi.post("/user/getTypeofuserData")
##博客Admin权限管理
async def UserPrivilegeName(request: Request, ):
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
                select(UserPrivileges.NameId, UserPrivileges.privilegeName).distinct()
            )
            privilege_values = privileges.all()

            # 将数据转换为 {id: 'name'} 的形式
            privilege_map = {privilege.NameId: privilege.privilegeName for privilege in privilege_values}
            print(privilege_map)
            return {"code": 20000, "data": privilege_map}
        except NoResultFound:
            return {"code": 20000, "data": {}}


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


@AdminApi.post('/Blogtaglist')
async def BlogTagList():
    async with db_session() as session:
        try:
            sql = select(models.BlogTag)
            result = await session.execute(sql)

            # 使用字典将相同 blog_id 的标签聚合到一起
            enddata = {}
            for tag in result.scalars().all():
                if tag.blog_id not in enddata:
                    sql2 = select(models.Blog).filter_by(BlogId=tag.blog_id)
                    blogresult = await session.execute(sql2)
                    blogname = blogresult.scalars().first()

                    if blogname:
                        enddata[tag.blog_id] = {
                            'Blog_id': tag.blog_id,
                            'Blog_title': blogname.title,
                            'Date': blogname.created_at.strftime('%Y-%m-%d'),
                            'Tags': [tag.Article_Type]  # 初始化标签列表
                        }
                else:
                    # 如果该标签不在已有标签列表中，添加它
                    if tag.Article_Type not in enddata[tag.blog_id]['Tags']:
                        enddata[tag.blog_id]['Tags'].append(tag.Article_Type)

            return {"data": enddata, "code": 20000}
        except jwt.ExpiredSignatureError:
            return {"code": 50012, "message": "Token已过期"}
        except jwt.InvalidTokenError:
            return {"code": 40003, "message": "无效的Token"}
        except Exception as e:
            return {"code": 50000, "message": "内部服务器错误", "error": str(e)}


# 从文章中创建Tag
@AdminApi.post('/Blogtagcreate/{blog_id}/{type}')
async def BlogTagcreate(data: BlogTagModel):
    async with db_session() as session:
        try:
            new_type = models.BlogTag(Article_Type=data.Article_Type, blog_id=data.blog_id,
                                      tag_created_at=data.tag_created_at)
            session.add(new_type)
            await session.commit()
            return {"data": new_type, "code": 20000}
        except jwt.ExpiredSignatureError:
            return {"code": 50012, "message": "Token已过期"}
        except jwt.InvalidTokenError:
            return {"code": 40003, "message": "无效的Token"}
        except Exception as e:
            return {"code": 50000, "message": "内部服务器错误"}


@AdminApi.post('/Newtagcreate/')
async def NewTagcreate(data: BlogTagModel):
    async with db_session() as session:
        try:
            # 查询是否已经存在相同名字的tag
            existing_tag_query = select(models.BlogTag).where(
                models.BlogTag.Article_Type == data.Article_Type,
                models.BlogTag.blog_id == data.Blog_id if data.Blog_id != 'None' else None
            )
            existing_tag = await session.execute(existing_tag_query)
            existing_tag = existing_tag.scalar_one_or_none()

            if existing_tag:
                return {"code": 40002, "message": "该文章已存在相同名字的tag"}

            # 如果没有找到重复的tag，则添加新tag
            if data.Blog_id == 'None':
                new_type = models.BlogTag(
                    Article_Type=data.Article_Type,
                    tag_created_at=data.tag_created_at
                )
            else:
                new_type = models.BlogTag(
                    Article_Type=data.Article_Type,
                    tag_created_at=data.tag_created_at,
                    blog_id=data.Blog_id
                )

            session.add(new_type)
            await session.commit()
            return {"data": "添加新Tag成功", "code": 20000}

        except IntegrityError:
            return {"code": 40001, "message": "请检查 blog_id 是否存在"}
        except jwt.ExpiredSignatureError:
            return {"code": 50012, "message": "Token已过期"}
        except jwt.InvalidTokenError:
            return {"code": 40003, "message": "无效的Token"}
        except Exception as e:
            print(e)
            return {"code": 50000, "message": "内部服务器错误"}


@AdminApi.post('/Blogtagmodify/{blog_id}/{type}')
async def BlogTagModify(blog_id: int, type: str, ):
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

aliOssPrivateDocument = AliOssPrivateDocument()


@AdminApi.get('/blogseo/googleoauth2')
async def url_sent(background_tasks: BackgroundTasks, ):
    try:
        background_tasks.add_task(publish_url_notification)
        return {"data": "请求已经发送", "code": 20000}
    except Exception as e:
        print("我们遇到了下面的问题", {"data": str(e)})


@AdminApi.get('/blogseo/bingtest')
async def bing_url_notfication():
    url = "https://api.indexnow.org/indexnow"

    headers = {
        "Content-Type": "application/json; charset=utf-8",
    }

    payload = {
        "host": "blog.exploit-db.xyz",
        "key": "key",
        "keyLocation": "key",
        "urlList": ["https://blog.exploit-db.xyz"]
    }
    # 将payload转换为JSON格式
    json_payload = json.dumps(payload)
    # 发送POST请求
    response = requests.post(url, headers=headers, data=json_payload)
    # 打印响应
    print(response.url)
    return response.status_code


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
                JSON_KEY_FILE = json.loads(JSON_KEY_FILE_str.replace("'", '"').replace('\r\n', '\\r\\n'), strict=False)
                SCOPES = ['https://www.googleapis.com/auth/indexing']
                ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
                print(SCOPES)
                credentials = ServiceAccountCredentials.from_json_keyfile_dict(JSON_KEY_FILE, scopes=SCOPES)
                http = credentials.authorize(httplib2.Http())
                content = {
                    "url": blog_url,
                    "type": "URL_UPDATED",
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


@AdminApi.post('/markdown/uploadimg/')
async def markdown_img_upload(file: UploadFile = File(...), ):
    x = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    waitmarkdownimg = await file.read()
    # 创建 AliOssBlogMarkdownImg 的实例
    oss_client = AliOssBlogMarkdownImg()
    # 调用实例方法上传图片
    image_url = await oss_client.upload_bitsfile_markdown_img(bitsfile=waitmarkdownimg, current_blogimgconunt=x)
    return {"code": 20000, "msg": "图片上传成功", "file": file.filename, "url": image_url}


@AdminApi.post("/blog/Blogtagget")
# 博客AdminTag获取
async def AdminBlogTagget():
    async with db_session() as session:
        try:
            sql = select(models.BlogTag)
            result = await session.execute(sql)
            tags = result.scalars().all()
            return {"code:": 20000, "data:": tags}
        except jwt.ExpiredSignatureError:
            return {"code": 50012, "message": "Token已过期"}
        except jwt.InvalidTokenError:
            return {"code": 40003, "message": "无效的Token"}
        except Exception as e:
            return {"code": 50000, "message": "内部服务器错误"}


@AdminApi.post("/blog/Blogeditimg")
async def AdminBlogidADDimg(blog_id: int, file: UploadFile = File(...), ):
    async with db_session() as session:
        try:
            file = await file.read()
            fileurl = await uploadoss.upload_bitsfile(blogid=blog_id, bitsfile=file)
            result = await session.execute(select(Blog).filter(Blog.BlogId == blog_id))
            now = result.scalars().first()

            if now is None:
                print("数据库中还没有对应ID图片，进行新建")
                return {
                    "code": 20000,
                    "data": {
                        "msg": fileurl
                    }
                }
            else:
                print("数据库中存在对应ID图片，进行修改")
                update_stmt = update(Blog).where(Blog.BlogId == blog_id).values(BlogIntroductionPicture=fileurl)
                # 执行更新操作
                await session.execute(update_stmt)
                await session.commit()  # 提交事务以保存更改
                return {
                    "code": 20000,
                    "data": {
                        "msg": fileurl
                    }
                }
        except Exception as e:
            print(f"我们遇到了下面的错误{e}")
            return {"code": 50000, "message": "服务器错误"}


@AdminApi.post("/blog/Blogedit")
##博客对应ID编辑
async def AdminBlogidedit(blog_id: int, blog_edit: BlogCreate):
    async with db_session() as session:
        try:
            # 提取标签信息
            tags = blog_edit.tags

            # 根据 BlogId 查询相应的博客
            result = await session.execute(select(Blog).filter(Blog.BlogId == blog_id))
            blog_entry = result.scalar_one()

            # 更新博客内容
            for key, value in blog_edit.dict().items():
                if key == 'content':
                    # 编码字符串为二进制
                    setattr(blog_entry, key, bytes(value, encoding='utf-8'))
                else:
                    setattr(blog_entry, key, value)

            # 提交事务
            await session.flush()

            blog_id = blog_entry.BlogId
            # 创建对应的博客标签
            for tag in tags:
                blog_tag = BlogTag(Article_Type=tag, blog_id=blog_id)
                session.add(blog_tag)

            await session.commit()
            return {"code": 20000, "message": "更新成功"}
        except Exception as e:
            print("遇到了问题")
            print(e)
            await session.rollback()  # 发生错误时回滚事务
            return {"code": 50000, "message": "更新失败"}


@AdminApi.post("/blog/Blogid")
##博客对应ID内容查询
async def AdminBlogid(blog_id: int, ):
    async with db_session() as session:
        try:
            results = await session.execute(select(Blog).filter(Blog.BlogId == blog_id))
            data = results.scalars().all()
            data = [item.to_dict() for item in data]
            return {"code": 20000, "data": data}
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
        return []


@AdminApi.delete("/blog/BlogDel")
##博客Admin删除
async def AdminBlogDel(blog_id: int):
    async with db_session() as session:
        try:
            result = await session.execute(select(Blog).where(Blog.BlogId == blog_id))
            original = result.scalars().first()
            await session.delete(original)
            await session.commit()
            return {"code": 20000, "message": "删除成功", "success": True}
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail={"code": 50014})
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail={"code": 50014})


@AdminApi.post("/blog/BlogCreate")
##博客Admin创建文章
async def AdminBlogCreate(blog_create: BlogCreate):
    async with db_session() as session:
        try:
            content = blog_create.content.encode('utf-8')  # 将content字段转换为字节
            blog_create.content = content  # 更新blog_create中的content值
            # 提取标签信息
            tags = blog_create.tags
            # 创建博客文章
            blog_data = blog_create.dict(exclude={'tags'})  # 排除'tags'字段
            blog = Blog(**blog_data)
            session.add(blog)
            await session.flush()  # 获取插入记录后的自增值
            blog_id = blog.BlogId
            # 创建对应的博客标签
            for tag in tags:
                blog_tag = BlogTag(Article_Type=tag, blog_id=blog_id)
                session.add(blog_tag)
            await session.commit()
            return {"code": 20000, "message": "更新成功"}
        except jwt.ExpiredSignatureError:
            return {"code": 50012, "message": "Token已过期", "error": "Token已经过期"}
        except jwt.InvalidTokenError:
            return {"code": 40003, "message": "无效的Token"}
        except IntegrityError as e:
            # 处理标签重复或其他数据库完整性错误
            print("数据库完整性错误:", e)
            return {"code": 40001, "message": "标签重复或其他数据库完整性错误"}
        except Exception as e:
            print(e)
            raise HTTPException(status_code=401, detail={"code": 50014, "message": "Token验证出现问题"})


# 超级用户文章管理界面
@AdminApi.get("/blog/AdminBlogIndex")
async def AdminBlogIndex():
    async with db_session() as session:
        try:
            results = await session.execute(select(Blog))
            if results is not None:
                data = results.scalars().all()
                data = [item.to_dict() for item in data]

                return {"code": 20000, "data": data}
            else:
                return {"code": 20001, "message": "未找到数据"}
        except Exception as e:
            print("我们遇到了下面的问题")
            print(e)
            return {"code": 50000, "message": "内部服务器错误"}
