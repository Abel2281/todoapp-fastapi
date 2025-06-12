from fastapi import FastAPI
from database import engine
import models
from routers import todo, user, authentication as auth, chat


app = FastAPI()


models.Base.metadata.create_all(bind=engine)

app.include_router(chat.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(todo.router)
