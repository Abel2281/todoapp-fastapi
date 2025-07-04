from pydantic import BaseModel
from datetime import date

class User(BaseModel):
    username: str
    email: str
    id: int

class UserCreate(User):
    password: str

class signup(BaseModel):
    username: str
    email: str
    password: str
class UserLogin(BaseModel):
    email: str
    password: str
class UserResponse(User):
    class Config:
        orm_mode = True
    

class TodoBase(BaseModel):
    title: str
    description: str | None = None
    due_time: date

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_time: date | None = None
    is_completed: bool | None = None

class OwnerInfo(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


class TodoResponse(TodoBase):
    id: int
    is_completed: bool
    owner: OwnerInfo
    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None