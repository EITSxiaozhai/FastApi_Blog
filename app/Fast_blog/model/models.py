import asyncio
import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, MetaData, LargeBinary, DATETIME
from sqlalchemy.orm import relationship
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
    choices = [
        ('0', 'woman'),
        ('1', 'man'),
        ('2', 'NULL')
    ]
    __tablename__ = "usertable"
    __table_args__ = {'extend_existing': True}
    UserId = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True)
    userpassword = Column(PasswordType(schemes=['pbkdf2_sha256']))
    gender = Column(ChoiceType(choices), default="O")
    creation_time = Column(DateTime, default=datetime.datetime.now)
    Last_Login_Time = Column(DateTime, default=datetime.datetime.now)
    UserUuid = Column(String(255))
    UserEmail = Column(EmailType(255))

    def to_dict(self):
        return dict(UserId=self.UserId, username=self.username, userpassword=self.userpassword, gender=self.gender,
                    UserEmail=self.UserEmail, UserUuid=self.UserUuid)


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
    created_at = Column(DateTime)
    NumberLikes = Column(Integer)
    NumberViews = Column(Integer)
    author = Column(String(255))
    admin_id = Column(Integer, ForeignKey('Admintable.UserId'))

    def to_dict(self):
        return dict(BlogId=self.BlogId, title=self.title, content=self.content, author=self.author,
                    BlogIntroductionPicture=self.BlogIntroductionPicture, created_at=self.created_at)


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
