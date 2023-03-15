from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from  sqlalchemy.orm import sessionmaker
from urllib import  parse
import  sys


sys.path.append('../')

password = parse.quote("@XU15964352xu")
##使用utf8进行中文输入
Sql_URL = "mysql://django:"+ password + "@mysql.exploit-db.xyz/Fastapi_blog" + "?charset=utf8"
engine = create_engine(Sql_URL)
SessionLocal = sessionmaker(bind=engine,autocommit=False,autoflush=False)
Base = declarative_base()