from fastapi import APIRouter, HTTPException, Depends, status
import models,database,schemas
from sqlalchemy.orm import Session
import schemas, oauth2

router = APIRouter(
    tags=['User'],
    prefix='/user'
)

# Get all users
@router.get('/', response_model=list[schemas.UserResponse])
def get_all_users(db: Session = Depends(database.get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    users = db.query(models.User).all()
    if not users:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'No users found')
    return users


# Get user by id
@router.get('/{id}', response_model=schemas.UserResponse)
def get_user_by_id(id: int, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f'User with id {id} not found')
    return user