from fastapi import FastAPI
from starlette.responses import JSONResponse
from Fast_blog.database.database import engine
from sqlalchemy.orm import sessionmaker
from fastapi.staticfiles import StaticFiles
from app.Fast_blog.apps import AdminApp
from Fast_blog.apps import User_app
from Fast_blog.apps import Blog_app
from Fast_blog.apps import Power_Crawl
from Fast_blog.apps import SystemMonitoring
from fastapi.middleware.cors import CORSMiddleware

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

app = FastAPI()

app.include_router(User_app.UserApp, prefix='/api/generaluser', tags=["普通用户页面"])
app.include_router(Blog_app.BlogApp, prefix='/api', tags=["博客游客浏览页面"])
app.include_router(AdminApp.AdminApi, prefix='/api', tags=["超级用户管理页面"])
app.include_router(Power_Crawl.PowerApp, prefix='/api/power', tags=["电力爬虫页面"])
app.include_router(SystemMonitoring.MonitoringApp,prefix='/api/monitoring',tags=["系统监控页面"])

app.mount("/static", StaticFiles(directory="./Fast_blog/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    response_data = {"message": "hahahah"}
    return JSONResponse(content=response_data)
