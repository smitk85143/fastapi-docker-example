from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from enum import Enum
from typing import Optional
from typing_extensions import Annotated

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

class Item(BaseModel):
    id: int
    slug: str
    name: str
    price: float
    description: str | None = None

class User(BaseModel):
    email: EmailStr
    password: str

class ResponseUser(BaseModel):
    email: EmailStr
    created_at: datetime

    class Config:
        orm_model = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None

class Post(BaseModel):
    title: str
    content: str
    published: bool = False

class ResponsePost(Post):
    id: int
    user_id: int
    user: ResponseUser
    created_at: datetime

    class Config:
        orm_model = True

class Vote(BaseModel):
    post_id: int
    dir: Annotated[int, Field(le=1)]