from pydantic import BaseModel,EmailStr
from  typing import Optional
import  sys
sys.path.append('../')

class Blog(BaseModel):
    title:str
    content:str
    Published:Optional[bool]
