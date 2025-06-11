from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session, joinedload
import database, schemas, models, oauth2
from datetime import datetime


get_db = database.get_db
TodoCreate = schemas.TodoCreate
TodoResponse = schemas.TodoResponse
TodoUpdate =  schemas.TodoUpdate

router = APIRouter(
    tags=['Todo']
)

# Create a todo
@router.post('/todo', response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(request: TodoCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    new_todo = models.Todo(**request.model_dump(), owner_id=current_user.id)      #Need to convert pydantic to sqlalchemy model
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

#Get todos grouped by completed
@router.get('/todo/completed', response_model=list[TodoResponse])
def get_completed_todos(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    query = db.query(models.Todo).filter(models.Todo.owner_id == current_user.id)
    if not query.first():
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f'No todos found for user with id {current_user.id}')
    query = query.filter(models.Todo.is_completed == True)
    todos = query.all()
    if not todos:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'No completed todos found')
    return todos

@router.get('/todo/incomplete', response_model=list[TodoResponse])
def get_incomplete_todos(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    todos = db.query(models.Todo).options(joinedload(models.Todo.owner)).filter(
    models.Todo.owner_id == current_user.id,
    models.Todo.is_completed == False
).all()
    if not todos:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'No incomplete todos found')
    return todos

@router.get('/todo/time_elapsed', response_model=list[TodoResponse])
def get_todos_time_elapsed(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    query = db.query(models.Todo).filter(
        models.Todo.owner_id == current_user.id,
        models.Todo.is_completed == False,
        models.Todo.due_time < datetime.now())
    if not query.first():
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f'No todos found ')
    now = datetime.now().date()
    query = query.filter(models.Todo.is_completed == False)
    elapsed_todos = elapsed_todos = query.all()

    if not elapsed_todos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No todos with time elapsed found'
        )

    return elapsed_todos

# Get todo by id
@router.get('/todo/{id}', response_model=TodoResponse)
def get_todo_by_id(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    todo = db.query(models.Todo).filter(models.Todo.id == id, models.Todo.owner_id==current_user.id).first()
    if not todo:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f'Todo with id {id} not found')
    return todo

# Update todo using id
@router.patch('/todo/{id}', response_model=TodoResponse, status_code=status.HTTP_200_OK)
def update_todo(id: int, request: TodoUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    data = request.model_dump(exclude_unset=True)
    todo = db.query(models.Todo).filter(models.Todo.id == id , models.Todo.owner_id==current_user.id).first()
    if not todo:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f'Todo with id {id} not found')
    for key,value in data.items():      # or todo.title = data.get('title, todo.title) etc
        setattr(todo, key, value)
    db.commit()
    db.refresh(todo)
    return todo

# Delete todo using id
@router.delete('/todo/{id}', status_code=status.HTTP_202_ACCEPTED)
def delete_todo(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    todo_query = db.query(models.Todo).filter(models.Todo.id == id , models.Todo.owner_id==current_user.id)
    todo = todo_query.first()
    if not todo:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f'Todo with id {id} not found')
    todo_query.delete(synchronize_session=False)
    db.commit()
    return {'detail': f'Todo with id {id} deleted successfully'}