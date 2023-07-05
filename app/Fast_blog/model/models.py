import asyncio
import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, MetaData,LargeBinary
from  sqlalchemy_utils import EmailType,ChoiceType
from app.Fast_blog.database.database import Base, engine
from dataclasses import dataclass


@dataclass
class User(Base):
    choices = [
        ('0', 'woman'),
        ('1', 'man'),
        ('2', 'NULL')
    ]
    __tablename__ = "usertable"
    __table_args__ = {'extend_existing': True}
    UserId = Column(Integer,primary_key = True,index = True)
    username = Column(String(255),unique=True)
    userpassword = Column(String(255))
    gender = Column(ChoiceType(choices))
    creation_time = Column(DateTime,default = datetime.datetime.now)
    Last_Login_Time = Column(DateTime,default= datetime.datetime.now)
    UserUuid = Column(String(255))
    UserEmail = Column(EmailType(255))
    def to_dict(self):
        return dict(UserId=self.UserId,username=self.username,userpassword=self.userpassword,gender=self.gender,UserEmail=self.UserEmail,UserUuid=self.UserUuid)

@dataclass
class Blog(Base):
    __tablename__ = "blogtable"
    __table_args__ = {'extend_existing': True}

    BlogId = Column(Integer,primary_key=True,index=True)
    title = Column(String(255))
    content = Column(LargeBinary)
    BlogIntroductionPicture = Column(String(255))
    author = Column(String(255))
    def to_dict(self):
        return dict(BlogId=self.BlogId,title=self.title,content=self.content,author=self.author,BlogIntroductionPicture=self.BlogIntroductionPicture)


@dataclass
class PowerMeters(Base):
    __tablename__ = "powertable"
    __table_args__ = {'extend_existing': True}
    PowerId = Column(Integer, primary_key=True, index=True)
    DataNum = Column(DateTime,default= datetime.datetime.now().strftime("%Y-%m-%d"))
    electricityNum = Column(String(255))
    PowerConsumption = Column(String(255))
    AveragePower = Column(String(255))
    def to_dict(self):
        return dict(DataNum=self.DataNum,electricityNum=self.electricityNum,PowerConsumption=self.PowerConsumption,AveragePower=self.AveragePower)