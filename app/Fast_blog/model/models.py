import asyncio
import datetime
from typing import List

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, MetaData, LargeBinary, DATETIME, Float, \
    UniqueConstraint, Text
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy_utils import EmailType, ChoiceType, PasswordType, Choice
from app.Fast_blog.database.database import Base, engine
from dataclasses import dataclass


@dataclass
class UserPrivileges(Base):
    Typeofuserchoices = [
        ('admin', 'admin'),
        ('editer', 'editer'),
        ('NULL', 'NULL')
    ]
    __tablename__ = "AdminPrivileges"
    __table_args__ = {'extend_existing': True}
    NameId = Column(Integer, primary_key=True, index=True)
    privilegeName = Column(ChoiceType(Typeofuserchoices), default="1")


@dataclass
class User(Base):
    ActivationStateType = [
        ('YA', 'Activated'),
        ('NA', 'Pending Activation'),
        ('NULL', 'NULL')
    ]
    __tablename__ = "usertable"
    __table_args__ = {'extend_existing': True}
    UserId = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True)
    userpassword = Column(PasswordType(schemes=['pbkdf2_sha256']))
    creation_time = Column(DateTime, default=datetime.datetime.now)
    Last_Login_Time = Column(DateTime, default=datetime.datetime.now)
    UserUuid = Column(String(255))
    UserEmail = Column(EmailType(255))
    UserAvatar = Column(String(255), unique=True)
    comments = relationship("Comment", back_populates="user")
    ActivationCode = Column(Integer, default=None)
    ActivationState = Column(ChoiceType(ActivationStateType), default="NA")

    def to_dict(self):
        return dict(UserId=self.UserId, username=self.username, userpassword=self.userpassword,
                    UserEmail=self.UserEmail, UserUuid=self.UserUuid,ActivationCode=self.ActivationCode, ActivationState=self.ActivationState)


@dataclass
class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    parentId = Column(Integer, ForeignKey('comments.id'), nullable=True)

    uid = Column(Integer, ForeignKey('usertable.UserId'))
    blog_id = Column(Integer, ForeignKey('blogtable.BlogId'))
    blog = relationship("Blog", back_populates="comments")
    address = Column(String(255))
    content = Column(String(255), nullable=False)  # 修改此行，为 content 指定长度
    likes = Column(Integer, default=0)
    createTime = Column(DateTime, default=datetime.datetime.now)  # 修改此行，为 createTime 指定长度
    contentImg = Column(String(255))  # 修改此行，为 contentImg 指定长度
    user = relationship("User", back_populates="comments")
    replies = relationship("Comment", backref="parent_comment", remote_side=[id])

    def to_dict(self):
        return dict(parentId=self.parentId, uid=self.uid, blog_id=self.blog_id, content=self.content, likes=self,
                    createTime=self.createTime, contentImg=self.contentImg, user=self.user, replies=self.replies)


@dataclass
class AdminUser(Base):
    choices = [
        ('0', 'woman'),
        ('1', 'man'),
        ('2', 'NULL')
    ]
    __tablename__ = "Admintable"
    __table_args__ = {'extend_existing': True}
    UserId = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True)
    userpassword = Column(PasswordType(schemes=['pbkdf2_sha256']))
    gender = Column(ChoiceType(choices), default="2")
    creation_time = Column(DateTime, default=datetime.datetime.now)
    Last_Login_Time = Column(DateTime, default=datetime.datetime.now)
    UserUuid = Column(String(255))
    UserEmail = Column(EmailType(255))
    userPrivileges = Column(Integer, ForeignKey('AdminPrivileges.NameId'))
    privileges = relationship("UserPrivileges", foreign_keys=[userPrivileges], lazy="select")

    def to_dict(self):
        return dict(UserId=self.UserId, username=self.username, gender=self.gender, UserEmail=self.UserEmail,
                    UserUuid=self.UserUuid, userPrivileges=self.userPrivileges)


@dataclass
class Blog(Base):
    __tablename__ = "blogtable"
    __table_args__ = {'extend_existing': True}

    BlogId = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    content = Column(LargeBinary)
    BlogIntroductionPicture = Column(String(255))
    created_at = Column(DateTime, default=datetime.datetime.now)
    NumberLikes = Column(Integer)
    NumberViews = Column(Integer)
    author = Column(String(255))
    BlogTags = relationship("BlogTag", back_populates="blogs", primaryjoin="Blog.BlogId == BlogTag.blog_id")
    admin_id = Column(Integer, ForeignKey('Admintable.UserId'))
    ratings = relationship("BlogRating", back_populates="blog")
    comments = relationship("Comment", back_populates="blog")

    def to_dict(self):
        return dict(BlogId=self.BlogId, title=self.title, content=self.content, author=self.author,
                    BlogIntroductionPicture=self.BlogIntroductionPicture, created_at=self.created_at)


class BlogTag(Base):
    __tablename__ = "blogtag"
    __allow_unmapped__ = True
    id = Column(Integer, primary_key=True, index=True)
    Article_Type = Column(String(255), index=True)
    tag_created_at = Column(DateTime, default=datetime.datetime.now)
    blog_id = Column(Integer, ForeignKey('blogtable.BlogId'))
    blogs = relationship("Blog", back_populates="BlogTags", primaryjoin="BlogTag.blog_id == Blog.BlogId", uselist=True)

    def to_dict(self):
        return dict(blog_id=self.blog_id, id=self.id, blog_type=self.Article_Type,
                    tag_created_at=self.tag_created_at.timestamp(),
                    Related_Blogs=[blog.to_dict() for blog in self.blogs])


@dataclass
class PowerMeters(Base):
    __tablename__ = "powertable"
    __table_args__ = {'extend_existing': True}
    PowerId = Column(Integer, primary_key=True, index=True)
    DataNum = Column(DateTime, default=datetime.datetime.now().strftime("%Y-%m-%d"))
    electricityNum = Column(String(255))
    PowerConsumption = Column(String(255))
    AveragePower = Column(String(255))

    def to_dict(self):
        return dict(DataNum=self.DataNum, electricityNum=self.electricityNum, PowerConsumption=self.PowerConsumption,
                    AveragePower=self.AveragePower)

@dataclass
class BlogRating(Base):
    __tablename__ = "blog_ratings"
    id = Column(Integer, primary_key=True, index=True)
    blog_id = Column(Integer, ForeignKey("blogtable.BlogId"))
    rating = Column(Float)
    blog = relationship("Blog", back_populates="ratings")

    def to_dict(self):
        return dict(blog_id=self.blog_id, rating=self.rating, blog=self.blog)

@dataclass
class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(255), index=True)  # 指定了长度为 255 字符
    blog_id = Column(String(255), index=True)
    vote_count = Column(Integer, default=0)
    __table_args__ = (UniqueConstraint('device_id', 'blog_id'),)

@dataclass
class ReptileInclusion(Base):
    __tablename__ = "ReptileInclusion"
    id = Column(Integer,primary_key=True, index=True)
    blog_id = Column(Integer, ForeignKey("blogtable.BlogId"))
    GoogleSubmissionStatus = Column(String(255))
    BingSubmissionStatus = Column(String(255))
    Submissiontime = Column(DateTime,default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    ReturnLog = Column(Text)

    def to_dict(self):
        return dict(id=self.id, blog_id=self.blog_id, GoogleSubmissionStatus=self.googleSubmissionStatus, BingSubmissionStatus=self.bingSubmissionStatus, Submissiontime=self.Submissiontime)
