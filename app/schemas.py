from pydantic import BaseModel
from datetime import datetime

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
    due_time: datetime

class TodCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_time: datetime | None = None
    is_completed: bool | None = None

class OwnerInfo(BaseModel):
    id: int
    username: str

class TodoResponse(TodoBase):
    id: int
    is_completed: bool
    owner_id: OwnerInfo
    class Config:
        orm_mode = True