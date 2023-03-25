# ----- coding: utf-8 ------
# author: YAO XU time:
from fastapi import APIRouter
import bs4
import requests
from bs4 import BeautifulSoup
from app.Fast_blog.database.database import db_session



PowerApp = APIRouter()



@PowerApp.post('/')
# 电力数据爬取入库
async def LetView(request):
    async with db_session() as session:
        res = requests.post(
            url='http://www.wap.cnyiot.com/(S(mjfpk2lgscja02m00mcj3otd))/nat/pay.aspx?mid=19500357280&chInfo=ch_share__chsub_CopyLink&apshareid=7cad8ac6-7aed-4391-b02f-23a9d11fbe37')
        # rex = requests.post(url='http://www.wap.cnyiot.com/(S(jd2c1lijcm5pmagoyoyqr2yk))/nat/pay.aspx?Method=getpayfee')
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        x = soup.find_all("label")
        end = x[1].string
        print(end)