import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
import  sys
from app.Fast_blog.database.database import Base
from  sqlalchemy_utils import EmailType,ChoiceType
sys.path.append('../')

class user(Base):
    choices = [
        ('0', 'woman'),
        ('1', 'man'),
        ('2', 'NULL')
    ]
    __tablename__ = "usertable"
    __table_args__ = {'extend_existing': True}
    UserId = Column(Integer,primary_key = True,index = True)
    username = Column(String(255))
    userpassword = Column(String(255))
    gender = Column(ChoiceType(choices))
    creation_time = Column(DateTime,default = datetime.datetime.now)
    Last_Login_Time = Column(DateTime,default= datetime.datetime.now)
    UserUuid = Column(String(255))
    UserEmail = Column(EmailType(255))

class Blog(Base):
    __tablename__ = "blogtable"
    __table_args__ = {'extend_existing': True}
    title = Column(String(255))
    content = Column(String(255))
    author = Column(String(255))
    BlogId = Column(String(255),primary_key=True,index=True)
    BlogUuid = Column(String(32))