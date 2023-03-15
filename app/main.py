

from  fastapi import  FastAPI,Path,Request
from  Fast_blog.database.database import engine

from Fast_blog.model import models
from sqlalchemy.orm import sessionmaker
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from Fast_blog.apps import User_app
from Fast_blog.apps import Blog_app
models.Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
session = SessionLocal()

app = FastAPI()
app.include_router(User_app.UserApp,prefix='/user')
app.include_router(Blog_app.BlogApp,prefix='/blog')


templates = Jinja2Templates(directory="./Fast_blog/templates")

app.mount("/static", StaticFiles(directory="./Fast_blog/static"), name="static")





@app.get("/")
async def root():
    return {"message":"Hello Word"}

