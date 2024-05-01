from fastapi import status, Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from utils import get_password_hash
import models, schemas

router = APIRouter(tags=['User'])

@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.ResponseUser)
def create_user(user: schemas.User, db: Session = Depends(get_db)):
    user.password = get_password_hash(user.password)
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/users/{user_id}", response_model=schemas.ResponseUser)
def get_post_by_id(user_id: int, db: Session = Depends(get_db)):
    data = db.query(models.User).filter(models.User.id == user_id).first()
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {user_id} was not found")
    return data