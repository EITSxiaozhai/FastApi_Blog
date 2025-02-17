from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, constr, Field


class UserCredentials(BaseModel):
    username: str
    password: str
    googlerecaptcha: str


class UserRegCredentials(BaseModel):
    username: str
    password: str
    confirmpassword: str
    googlerecaptcha: str
    email: EmailStr
    EmailverificationCod: int
    UserAvatar: Optional[str] = Field(
        default="https://bkimg.cdn.bcebos.com/pic/a2cc7cd98d1001e952722fb2ba0e7bec55e797c4?x-bce-process=image/format,f_auto/watermark,image_d2F0ZXIvYmFpa2UyNzI,g_7,xp_5,yp_5,P_20/resize,m_lfit,limit_1,h_1080")


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
    username: str
    userpassword: constr(min_length=8)
    UserEmail: EmailStr
    gender: str
    userprivilegesData: int


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
    Blog_id: Optional[str] = Field(...)
    Article_Type: Optional[str]
    tag_created_at: datetime = datetime.now()


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
    publishStatus: bool
