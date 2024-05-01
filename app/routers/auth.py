from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from database import get_db
from sqlalchemy.orm import Session
from schemas import UserLogin
import models
from utils import verify_password
from oauth2 import create_access_token
from schemas import Token

router = APIRouter(tags=['Authentication'])

@router.post("/login", response_model=Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Invaild Credentials")
    
    if not verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invaild Credentials")
    
    access_token = create_access_token(data={'user_id': user.id})

    return {"access_token": access_token, "token_type": "bearer"}