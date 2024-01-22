from datetime import datetime

from fastapi import UploadFile
from pydantic import BaseModel, EmailStr,FileUrl
from typing import Optional
import sys

sys.path.append('../')


class UserCredentials(BaseModel):
    username: str
    password: str
    googlerecaptcha: str

class UserRegCredentials(BaseModel):
    username: str
    password: str
    confirmpassword : str
    googlerecaptcha: str
    email: EmailStr
    EmailverificationCod : int
    UserAvatar: FileUrl



class Token(BaseModel):
    access_token: str
    token_type: str


class Blog(BaseModel):
    title: str
    content: str
    Published: Optional[bool]


class SchemasUser(BaseModel):
    inusername: str
    inuserpassword: str
    gender: bool
    UserUuid: str
    UserEmail: EmailStr


from typing import Optional, List
from pydantic import BaseModel, EmailStr, constr


class UserPrivilegesModel(BaseModel):
    NameId: int
    privilegeName: str


class UserModel(BaseModel):
    UserId: int
    username: str
    userpassword: constr(min_length=8)  # 设置最小密码长度
    gender: str
    creation_time: datetime
    Last_Login_Time: datetime
    UserUuid: str
    UserEmail: EmailStr
    comments: List[Optional["CommentModel"]] = []


class CommentModel(BaseModel):
    id: int
    parentId: Optional[int]

    uid: int
    blog_id: int
    address: str
    content: str
    likes: int
    createTime: str
    contentImg: str
    user: Optional[UserModel]
    replies: List[Optional["CommentModel"]] = []


class AdminUserModel(BaseModel):
    UserId: int
    username: str
    userpassword: constr(min_length=8)
    gender: str
    creation_time: datetime
    Last_Login_Time: datetime
    UserUuid: str
    UserEmail: EmailStr
    userPrivileges: Optional[int]
    privileges: Optional[UserPrivilegesModel]


class BlogModel(BaseModel):
    BlogId: int
    title: str
    content: bytes
    BlogIntroductionPicture: str
    created_at: datetime
    NumberLikes: int
    NumberViews: int
    author: str
    admin_id: int
    ratings: List[Optional["BlogRatingModel"]] = []
    comments: List[Optional[CommentModel]] = []


class PowerMetersModel(BaseModel):
    PowerId: int
    DataNum: datetime
    electricityNum: str
    PowerConsumption: str
    AveragePower: str


class BlogRatingModel(BaseModel):
    id: int
    blog_id: int
    rating: float
    blog: Optional[BlogModel]


class VoteModel(BaseModel):
    id: int
    device_id: str
    blog_id: str
    vote_count: int


class BlogTagModel(BaseModel):
    blog_id: int
    Article_Type: str
    tag_created_at: datetime



class CommentDTO(BaseModel):
    articleId: int
    content: str
    parentId: int

class BlogCreate(BaseModel):
    title: str
    content: str
    BlogIntroductionPicture: str
    author: str
    tags: List[str]
