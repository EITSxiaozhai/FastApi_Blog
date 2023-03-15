import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
import  sys
from app.Fast_blog.database.database import Base

sys.path.append('../')


class user(Base):
    __tablename__ = "usertable"
    __table_args__ = {'extend_existing': True}
    userid = Column(Integer,primary_key = True,index = True)
    username = Column(String(32))
    userpassword = Column(String(32))
    gender = Column(Boolean)
    creation_time = Column(DateTime,default = datetime.datetime.now())
    Last_Login_Time = Column(DateTime,default= datetime.datetime.now())


class Blog(Base):
    __tablename__ = "blogtable"
    __table_args__ = {'extend_existing': True}
    title = Column(String(255))
    content = Column(String(255))
    author = Column(String(255))
    id = Column(String(255),primary_key=True,index=True)