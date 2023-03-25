# ----- coding: utf-8 ------
# author: YAO XU time:
import DateTime
from fastapi import APIRouter
import bs4
import requests
import datetime
from app.Fast_blog.database.database import db_session
from app.Fast_blog.model import models
from app.Fast_blog.model.models import PowerMeters
from sqlalchemy import exists, select, func
PowerApp = APIRouter()



@PowerApp.get('/')
# 电力数据爬取入库
async def LetView():
    async with db_session() as session:
        try:
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            res = requests.post(
                url='http://www.wap.cnyiot.com/(S(mjfpk2lgscja02m00mcj3otd))/nat/pay.aspx?mid=19500357280&chInfo=ch_share__chsub_CopyLink&apshareid=7cad8ac6-7aed-4391-b02f-23a9d11fbe37')
            # rex = requests.post(url='http://www.wap.cnyiot.com/(S(jd2c1lijcm5pmagoyoyqr2yk))/nat/pay.aspx?Method=getpayfee')
            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            x = soup.find_all("label")
            end = x[1].string


            #进行数据库查询检测是否有当前日期
            stmt = select(PowerMeters).filter_by(DataNum = today)
            result = await session.execute(stmt)
            for i in result.scalars().all():
                print(i.__dict__['DataNum'])

            #判断并输出到前端页面
            if result.scalars().all() is not None:
                print("当前日期数据已经存在")
                return ({"数据存在日期:":i.__dict__['DataNum']})
            else:
                print("当前日期数据未存在")


        except Exception as e:
            print(e)



@PowerApp.get('/all')
# 电力数据全部输出
async def LetTest():
    async with db_session() as session:
        try:
            today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            res = requests.post(
                url='http://www.wap.cnyiot.com/(S(mjfpk2lgscja02m00mcj3otd))/nat/pay.aspx?mid=19500357280&chInfo=ch_share__chsub_CopyLink&apshareid=7cad8ac6-7aed-4391-b02f-23a9d11fbe37')
            # rex = requests.post(url='http://www.wap.cnyiot.com/(S(jd2c1lijcm5pmagoyoyqr2yk))/nat/pay.aspx?Method=getpayfee')
            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            x = soup.find_all("label")
            end = x[1].string
            sql = select(models.PowerMeters).where(models.User.gender is not None)
            results = await session.execute(sql)
            data = results.scalars().all()
            data = [item.to_dict() for item in data]
            print(data)
            return ({"data":data})
        except Exception as e:
            print(e)
            return ({"ERROR:":e})
