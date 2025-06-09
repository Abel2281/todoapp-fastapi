from pydantic import BaseModel
from datetime import date

class User(BaseModel):
    username: str
    email: str

class UserCreate(User):
    password: str

class UserResponse(User):
    id: int
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