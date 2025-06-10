from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session, joinedload
from app import database, schemas, models
from datetime import datetime

get_db = database.get_db
TodoCreate = schemas.TodoCreate
TodoResponse = schemas.TodoResponse
TodoUpdate =  schemas.TodoUpdate

router = APIRouter(
    tags=['Todo']
)

# Create a todo
@router.post('/todo', response_model=TodoCreate, status_code=status.HTTP_201_CREATED)
def create_todo(request: TodoCreate, db: Session = Depends(get_db)):
    new_todo = models.Todo(**request.model_dump(), owner_id=1)      #Need to convert pydantic to sqlalchemy model
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

#Get todos grouped by completed
@router.get('/todo/completed', response_model=list[TodoResponse])
def get_completed_todos(db: Session = Depends(get_db)):
    id = 1
    query = db.query(models.Todo).filter(models.Todo.owner_id == id)
    if not query.first():
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f'No todos found for user with id {id}')
    query = query.filter(models.Todo.is_completed == True)
    todos = query.all()
    if not todos:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'No completed todos found')
    return todos

@router.get('/todo/incomplete', response_model=list[TodoResponse])
def get_incomplete_todos(db: Session = Depends(get_db)):
    id = 1
    todos = db.query(models.Todo).options(joinedload(models.Todo.owner)).filter(
    models.Todo.owner_id == id,
    models.Todo.is_completed == False
).all()
    if not todos:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'No incomplete todos found')
    return todos

@router.get('/todo/time_elapsed', response_model=list[TodoResponse])
def get_todos_time_elapsed(db: Session = Depends(get_db)):
    id = 1
    query = db.query(models.Todo).filter(models.Todo.owner_id == id)
    if not query.first():
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f'No todos found for user with id {id}')
    now = datetime.now().date()
    query = query.filter(models.Todo.is_completed == False)
    elapsed_todos = [
        todo for todo in query if todo.due_time.date() < now
    ]

    if not elapsed_todos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No todos with time elapsed found'
        )

    return elapsed_todos

# Get todo by id
@router.get('/todo/{id}', response_model=TodoResponse)
def get_todo_by_id(id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == id).first()
    if not todo:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f'Todo with id {id} not found')
    return todo

# Update todo using id
@router.patch('/todo/{id}', response_model=TodoResponse, status_code=status.HTTP_200_OK)
def update_todo(id: int, request: TodoUpdate, db: Session = Depends(get_db)):
    data = request.model_dump(exclude_unset=True)
    todo = db.query(models.Todo).filter(models.Todo.id == id).first()
    if not todo:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f'Todo with id {id} not found')
    for key,value in data.items():      # or todo.title = data.get('title, todo.title) etc
        setattr(todo, key, value)
    db.commit()
    db.refresh(todo)
    return todo

# Delete todo using id
@router.delete('/todo/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(id: int, db: Session = Depends(get_db)):
    todo_query = db.query(models.Todo).filter(models.Todo.id == id)
    todo = todo_query.first()
    if not todo:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f'Todo with id {id} not found')
    todo_query.delete(synchronize_session=False)
    db.commit()
    return {'detail': f'Todo with id {id} deleted successfully'}