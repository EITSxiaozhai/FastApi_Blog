from pydantic import BaseModel,EmailStr
from  typing import Optional
import  sys
sys.path.append('../')



class Blog(BaseModel):
    title:str
    content:str
    Published:Optional[bool]





class SchemasUser(BaseModel):
    inusername:str
    inuserpassword:str
    gender:bool
    UserUuid:str
    UserEmail:EmailStr
