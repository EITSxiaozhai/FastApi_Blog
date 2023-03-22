import asyncio
import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import registry, sessionmaker
from  sqlalchemy_utils import EmailType,ChoiceType
from app.Fast_blog.database.database import Base, engine




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


class Blog(Base):
    __tablename__ = "blogtable"
    __table_args__ = {'extend_existing': True}
    BlogId = Column(Integer,primary_key=True,index=True)
    title = Column(String(255))
    content = Column(String(255))
    author = Column(String(255))
