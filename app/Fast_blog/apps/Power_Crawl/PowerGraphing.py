# ----- coding: utf-8 ------
# author: YAO XU time:
from fastapi import APIRouter
import bs4
import requests
import datetime

from sqlalchemy.ext.asyncio import AsyncSession


from app.Fast_blog.database.database import engine
from app.Fast_blog.database.database import db_session
from app.Fast_blog.middleware import celery_app
from app.Fast_blog.model import models
from app.Fast_blog.model.models import PowerMeters
from sqlalchemy import exists, select, func, cast, Date, desc


PowerApp = APIRouter()





##嵌套测试
@PowerApp.get('/find')
async def query_power():
    async with engine.begin() as conn:
        async with AsyncSession(engine, expire_on_commit=False) as session:
            #查询昨日信息数据
            today = datetime.date.today()
            yesterday = today - datetime.timedelta(days=1)
            ##查询昨日日期数据使用cast方法转换,并使用strfitme进行格式化转换
            stmt = select(PowerMeters).order_by(desc(PowerMeters.DataNum)).limit(1)
            AvgStmt = select(func.avg(PowerMeters.PowerConsumption))
            result = await session.execute(stmt)
            AvgResult = await  session.execute(AvgStmt)
            users = result.scalars().all()
            for TodayInfo in users:
                electricityNumToday = TodayInfo.electricityNum
                PowerConsumptionToday = TodayInfo.PowerConsumption
                return ({"electricityNumToday":electricityNumToday,"PowerConsumptionToday":round(float(PowerConsumptionToday),2),"AveragePower":round(AvgResult.scalars().first(),2)})





@celery_app.task
# 电力数据爬取入库
@PowerApp.get('/')
async def LetView():
    async with db_session() as session:
        try:
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            res = requests.post(
                url='http://www.wap.cnyiot.com/(S(mjfpk2lgscja02m00mcj3otd))/nat/pay.aspx?mid=19500357280&chInfo=ch_share__chsub_CopyLink&apshareid=7cad8ac6-7aed-4391-b02f-23a9d11fbe37')
            # rex = requests.post(url='http://www.wap.cnyiot.com/(S(jd2c1lijcm5pmagoyoyqr2yk))/nat/pay.aspx?Method=getpayfee')
            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            x = soup.find_all("label")
            if len(x) >= 2:
                end = x[1].string
                print(end)
            else:
                print("日期未找到")
            # 处理找不到第二个元素的情况
            #进行数据库查询检测是否有当前日期
            stmt = select(PowerMeters).filter_by(DataNum = today)
            result = await session.execute(stmt)
            TodayList = await query_power()
            print(TodayList)
            if result.scalars().all():
                print("当前日期数据已经存在")
                return ({"数据存在日期:":today})
            elif result.scalars().all() is not None:
                print("当前日期数据未存在")
                Let =  models.PowerMeters(DataNum=datetime.datetime.now().strftime("%Y-%m-%d"),electricityNum=end,PowerConsumption=round(float(TodayList['electricityNumToday']) - float(end),2),AveragePower=round(TodayList['AveragePower'],2))
                session.add(Let)
                await session.commit()
                return ({"今天数据已经添加到数据库:":end})
        except Exception as e:
            print(e)



@PowerApp.get('/all')
# 电力数据全部输出
async def LetTest():
    async with db_session() as session:
        try:
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            res = requests.post(
                url='http://www.wap.cnyiot.com/(S(mjfpk2lgscja02m00mcj3otd))/nat/pay.aspx?mid=19500357280&chInfo=ch_share__chsub_CopyLink&apshareid=7cad8ac6-7aed-4391-b02f-23a9d11fbe37')
            # rex = requests.post(url='http://www.wap.cnyiot.com/(S(jd2c1lijcm5pmagoyoyqr2yk))/nat/pay.aspx?Method=getpayfee')
            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            x = soup.find_all("label")
            end = x[1].string
            sql = select(models.PowerMeters).where(models.PowerMeters.PowerId is not None)
            results = await session.execute(sql)
            data = results.scalars().all()
            data = [item.to_dict() for item in data]
            print(data)
            return ({"data":data})
        except Exception as e:
            print(e)
            return ({"ERROR:":e})




# @PowerApp.get('/orm')
# # 电力数据爬取入库
# async def LetViewOrm():
#     async with AsyncSession(engine) as session:
#         try:
#             today = datetime.datetime.now().strftime("%Y-%m-%d")
#             res = requests.post(
#                 url='http://www.wap.cnyiot.com/(S(mjfpk2lgscja02m00mcj3otd))/nat/pay.aspx?mid=19500357280&chInfo=ch_share__chsub_CopyLink&apshareid=7cad8ac6-7aed-4391-b02f-23a9d11fbe37')
#             # rex = requests.post(url='http://www.wap.cnyiot.com/(S(jd2c1lijcm5pmagoyoyqr2yk))/nat/pay.aspx?Method=getpayfee')
#             soup = bs4.BeautifulSoup(res.text, 'html.parser')
#             x = soup.find_all("label")
#             end = x[1].string
#
#         except Exception as e:
#             print(e)



