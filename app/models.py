from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True , autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, unique=True, nullable=False)

    todos = relationship("Todo", back_populates="owner")

class Todo(Base):
        __tablename__ = 'todos'

        id = Column(Integer, primary_key=True, index=True, autoincrement=True)
        title = Column(String, index=True)
        description = Column(String, index=True)
        is_completed = Column(Boolean, default=False)
        due_time = Column(Date, nullable=True)
        owner_id = Column(Integer, ForeignKey('users.id'))

        owner = relationship("User", back_populates="todos")
