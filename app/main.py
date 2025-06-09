from fastapi import FastAPI
from database import engine, Base
import models

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

@app.get('/')
async def hello():
    return {'message': 'Hello, World!'}

@app.get('/hello/{name}')
async def hello_name(name: str):
    return {'message': f'Hello, {name}!'}