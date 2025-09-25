import datetime
from dataclasses import dataclass
from typing import List

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary, Float, \
    UniqueConstraint, Text, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy_utils import EmailType, ChoiceType, PasswordType

from Fast_blog.database.databaseconnection import Base


@dataclass
class UserPrivileges(Base):
    Typeofuserchoices = [
        ('admin', 'admin'),
        ('editer', 'editer'),
        ('NULL', 'NULL')
    ]
    __tablename__ = "AdminPrivileges"
    __table_args__ = {'extend_existing': True}
    NameId: int = Column(Integer, primary_key=True, index=True)
    privilegeName: str = Column(ChoiceType(Typeofuserchoices), default="1")
    admin_users: Mapped[list["AdminUser"]] = relationship("AdminUser", back_populates="privileges")

    def to_dict(self):
        return dict(NameId=self.NameId, privilegeName=self.privilegeName)


@dataclass
class User(Base):
    ActivationStateType = [
        ('YA', 'Activated'),
        ('NA', 'Pending Activation'),
        ('NULL', 'NULL')
    ]
    __tablename__ = "usertable"
    __table_args__ = {'extend_existing': True}
    UserId: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String(255), unique=True)
    userpassword: str = Column(PasswordType(schemes=['pbkdf2_sha256']))
    creation_time: datetime.datetime = Column(DateTime, default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    Last_Login_Time: datetime.datetime = Column(DateTime, default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    UserUuid: str = Column(String(255))
    UserEmail: str = Column(EmailType(255))
    UserAvatar: str = Column(String(255), unique=True)
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="user")
    ActivationCode: int = Column(Integer, default=None)
    ActivationState: str = Column(ChoiceType(ActivationStateType), default="NA")

    def to_dict(self):
        return dict(UserId=self.UserId, username=self.username, userpassword=self.userpassword,
                    creation_time=self.creation_time, Last_Login_Time=self.Last_Login_Time,
                    UserUuid=self.UserUuid, UserEmail=self.UserEmail, UserAvatar=self.UserAvatar,
                    ActivationCode=self.ActivationCode, ActivationState=self.ActivationState)



@dataclass
class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    parentId: int = Column(Integer, ForeignKey('comments.id'), nullable=True)
    uid: int = Column(Integer, ForeignKey('usertable.UserId'))
    blog_id: Mapped[int] = mapped_column(Integer, ForeignKey('blogtable.BlogId'))
    blog: Mapped["Blog"] = relationship("Blog", back_populates="comments")
    address: str = Column(String(255))
    content: str = Column(String(255), nullable=False)
    likes: int = Column(Integer, default=0)
    createTime: datetime.datetime = Column(DateTime, default=datetime.datetime.now)
    contentImg: str = Column(String(255))
    user: Mapped["User"] = relationship("User", back_populates="comments")
    replies: Mapped[List["Comment"]] = relationship(
        "Comment",
        backref="parent_comment",
        remote_side=[id]
    )

    def to_dict(self):
        return dict(id=self.id, parentId=self.parentId, uid=self.uid, blog_id=self.blog_id,
                    address=self.address, content=self.content, likes=self.likes,
                    createTime=self.createTime, contentImg=self.contentImg)


@dataclass
class AdminUser(Base):
    choices = [
        ('0', 'woman'),
        ('1', 'man'),
        ('2', 'NULL')
    ]
    __tablename__ = "Admintable"
    __table_args__ = {'extend_existing': True}
    UserId: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String(255), unique=True)
    userpassword: str = Column(PasswordType(schemes=['pbkdf2_sha256']))
    gender: str = Column(ChoiceType(choices), default="2")
    creation_time: datetime.datetime = Column(DateTime, default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    Last_Login_Time: datetime.datetime = Column(DateTime, default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    UserUuid: str = Column(String(255))
    UserEmail: str = Column(EmailType(255))
    userPrivileges: int = Column(Integer, ForeignKey('AdminPrivileges.NameId'))
    privileges: Mapped["UserPrivileges"] = relationship(
        "UserPrivileges",
        foreign_keys=[userPrivileges],
        lazy="select",
        back_populates="admin_users"  # 需要同时在 UserPrivileges 添加对应关系
    )

    def to_dict(self):
        return dict(UserId=self.UserId, username=self.username, userpassword=self.userpassword,
                    creation_time=self.creation_time, Last_Login_Time=self.Last_Login_Time,
                    UserUuid=self.UserUuid, UserEmail=self.UserEmail, userPrivileges=self.userPrivileges)


# @dataclass
# class Blog(Base):
#     __tablename__ = "blogtable"
#     __table_args__ = {'extend_existing': True}
#     BlogId: int = Column(Integer, primary_key=True, index=True)
#     title: str = Column(String(255))
#     content: bytes = Column(LargeBinary)
#     BlogIntroductionPicture: str = Column(String(255))
#     created_at: datetime.datetime = Column(DateTime, default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
#     NumberLikes: int = Column(Integer)
#     NumberViews: int = Column(Integer)
#     author: str = Column(String(255))
#     BlogTags: Mapped[List["BlogTag"]] = relationship(
#         "BlogTag",
#         back_populates="blogs",
#         primaryjoin="Blog.BlogId == BlogTag.blog_id"
#     )
#     admin_id: int = Column(Integer, ForeignKey('Admintable.UserId'))
#     ratings: list = relationship("BlogRating", back_populates="blog")
#     comments: list = relationship("Comment", back_populates="blog")
#     PublishStatus: bool = Column(Boolean, default=False)
#
#     def to_dict(self):
#         return dict(BlogId=self.BlogId, title=self.title, content=self.content,
#                     BlogIntroductionPicture=self.BlogIntroductionPicture, created_at=self.created_at,
#                     NumberLikes=self.NumberLikes, NumberViews=self.NumberViews, author=self.author,
#                     admin_id=self.admin_id, PublishStatus=self.PublishStatus)

@dataclass
class Blog(Base):
    __tablename__ = "blogtable"
    __table_args__ = {'extend_existing': True}

    # 使用 mapped_column 替代 Column
    BlogId: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[bytes] = mapped_column(LargeBinary)
    description: Mapped[str] = mapped_column(Text, nullable=True)  # 新增 description 字段
    BlogIntroductionPicture: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.datetime.now)  # 移除 strftime
    
    # 修改后定义（添加 nullable=False 和 default）
    NumberLikes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,  # 明确非空约束
        default=0,  # 设置默认值
        server_default="0"  # 可选：数据库层面的默认值
    )
    NumberViews: Mapped[int] = mapped_column(Integer)
    author: Mapped[str] = mapped_column(String(255))
    admin_id: Mapped[int] = mapped_column(Integer, ForeignKey('Admintable.UserId'))
    PublishStatus: Mapped[bool] = mapped_column(Boolean, default=False)

    # 修正关系定义（关键修改点）
    BlogTags: Mapped[List["BlogTag"]] = relationship(
        "BlogTag",
        back_populates="blogs",
        primaryjoin="Blog.BlogId == BlogTag.blog_id"
    )

    ratings: Mapped[List["BlogRating"]] = relationship(
        "BlogRating",
        back_populates="blog"
    )

    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="blog"
    )
    
    anonymous_comments: Mapped[List["AnonymousComment"]] = relationship(
        "AnonymousComment",
        back_populates="blog"
    )

    def to_dict(self):
        return {
            "BlogId": self.BlogId,
            "title": self.title,
            "content": self.content.decode('utf-8') if self.content else None,  # 二进制转字符串示例
            "description": self.description,  # 添加 description 到返回字典
            "BlogIntroductionPicture": self.BlogIntroductionPicture,
            "created_at": self.created_at.isoformat(),
            "NumberLikes": self.NumberLikes,
            "NumberViews": self.NumberViews,
            "author": self.author,
            "admin_id": self.admin_id,
            "PublishStatus": self.PublishStatus
        }


@dataclass
class BlogTag(Base):
    __tablename__ = "blogtag"
    __allow_unmapped__ = True
    id: int = Column(Integer, primary_key=True, index=True)
    Article_Type: str = Column(String(255), index=True)
    tag_created_at: datetime.datetime = Column(DateTime, default=datetime.datetime.now)
    blog_id: int = Column(Integer, ForeignKey('blogtable.BlogId'))
    blogs: list = relationship("Blog", back_populates="BlogTags", primaryjoin="BlogTag.blog_id == Blog.BlogId", uselist=True)

    def to_dict(self):
        return dict(id=self.id, Article_Type=self.Article_Type, tag_created_at=self.tag_created_at, blog_id=self.blog_id)


@dataclass
class PowerMeters(Base):
    __tablename__ = "powertable"
    __table_args__ = {'extend_existing': True}
    PowerId: int = Column(Integer, primary_key=True, index=True)
    DataNum: datetime.datetime = Column(DateTime, default=datetime.datetime.now().strftime("%Y-%m-%d"))
    electricityNum: str = Column(String(255))
    PowerConsumption: str = Column(String(255))
    AveragePower: str = Column(String(255))

    def to_dict(self):
        return dict(PowerId=self.PowerId, DataNum=self.DataNum, electricityNum=self.electricityNum,
                    PowerConsumption=self.PowerConsumption, AveragePower=self.AveragePower)


# @dataclass
# class BlogRating(Base):
#     __tablename__ = "blog_ratings"
#     id: int = Column(Integer, primary_key=True, index=True)
#     blog_id: int = Column(Integer, ForeignKey("blogtable.BlogId"))
#     ratings: Mapped[List["BlogRating"]] = relationship("BlogRating", back_populates="blog")
#     blog: 'Blog' = relationship("Blog", back_populates="ratings")
#
#     def to_dict(self):
#         return dict(id=self.id, blog_id=self.blog_id, rating=self.rating)

@dataclass
class BlogRating(Base):
    __tablename__ = "blog_ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    blog_id: Mapped[int] = mapped_column(Integer, ForeignKey("blogtable.BlogId"))
    rating: Mapped[float] = mapped_column(Float)

    blog: Mapped["Blog"] = relationship("Blog", back_populates="ratings")


@dataclass
class Vote(Base):
    __tablename__ = "votes"
    id: int = Column(Integer, primary_key=True, index=True)
    device_id: str = Column(String(255), index=True)
    blog_id: str = Column(String(255), index=True)
    vote_count: int = Column(Integer, default=0)
    __table_args__ = (UniqueConstraint('device_id', 'blog_id'),)
    def to_dict(self):
        return dict(id=self.id, device_id=self.device_id, blog_id=self.blog_id, vote_count=self.vote_count)


@dataclass
class ReptileInclusion(Base):
    __tablename__ = "ReptileInclusion"
    id: int = Column(Integer, primary_key=True, index=True)
    blog_id: int = Column(Integer, ForeignKey("blogtable.BlogId"))
    GoogleSubmissionStatus: str = Column(String(255))
    BingSubmissionStatus: str = Column(String(255))
    Submissiontime: datetime.datetime = Column(DateTime, default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    ReturnLog: str = Column(Text)

    def to_dict(self):
        return dict(id=self.id, blog_id=self.blog_id, GoogleSubmissionStatus=self.GoogleSubmissionStatus,
                    BingSubmissionStatus=self.BingSubmissionStatus, Submissiontime=self.Submissiontime)


@dataclass
class AnonymousComment(Base):
    """匿名用户评论表"""
    __tablename__ = "anonymous_comments"
    __table_args__ = {'extend_existing': True}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    parentId: int = Column(Integer, ForeignKey('anonymous_comments.id'), nullable=True)
    blog_id: Mapped[int] = mapped_column(Integer, ForeignKey('blogtable.BlogId'))
    blog: Mapped["Blog"] = relationship("Blog", back_populates="anonymous_comments")
    nickname: str = Column(String(100), nullable=False)  # 匿名用户昵称
    email: str = Column(String(255), nullable=True)  # 可选邮箱
    content: str = Column(Text, nullable=False)  # 评论内容
    likes: int = Column(Integer, default=0)  # 点赞数
    createTime: datetime.datetime = Column(DateTime, default=datetime.datetime.now)
    contentImg: str = Column(String(500), nullable=True)  # 评论图片
    address: str = Column(String(255), nullable=True)  # 用户地址
    is_anonymous: bool = Column(Boolean, default=True)  # 标识为匿名评论
    
    # 自引用关系，支持回复功能
    replies: Mapped[List["AnonymousComment"]] = relationship(
        "AnonymousComment",
        backref="parent_comment",
        remote_side=[id]
    )

    def to_dict(self):
        return dict(
            id=self.id, 
            parentId=self.parentId, 
            blog_id=self.blog_id,
            nickname=self.nickname,
            email=self.email,
            content=self.content, 
            likes=self.likes,
            createTime=self.createTime, 
            contentImg=self.contentImg,
            address=self.address,
            is_anonymous=self.is_anonymous
        )