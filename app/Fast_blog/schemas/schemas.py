from pydantic import BaseModel, EmailStr
from typing import Optional
import sys

sys.path.append('../')


class UserCredentials(BaseModel):
    username: str
    password: str
    googlerecaptcha: str



class Token(BaseModel):
    access_token: str
    token_type: str


class Blog(BaseModel):
    title: str
    content: str
    Published: Optional[bool]



class SchemasUser(BaseModel):
    inusername: str
    inuserpassword: str
    gender: bool
    UserUuid: str
    UserEmail: EmailStr
