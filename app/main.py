from fastapi import FastAPI
from database import engine
import models
from routers import todo, user, authentication as auth, chat
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


models.Base.metadata.create_all(bind=engine)



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or use ["http://127.0.0.1:8000"] for stricter control
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chat.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(todo.router)
