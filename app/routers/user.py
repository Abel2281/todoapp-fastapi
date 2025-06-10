from fastapi import APIRouter, HTTPException, Depends, status
import models,database,schemas
from sqlalchemy.orm import Session

router = APIRouter(
    tags=['User'],
    prefix='/user'
)

# Get all users
@router.get('/', response_model=list[schemas.UserResponse], tags=['User'])
def get_all_users(db: Session = Depends(database.get_db)):
    users = db.query(models.User).all()
    if not users:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'No users found')
    return users


# Get user by id
@router.get('/{id}', response_model=schemas.UserResponse, tags=['User'])
def get_user_by_id(id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f'User with id {id} not found')
    return user