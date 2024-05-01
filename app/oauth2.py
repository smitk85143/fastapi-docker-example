from jose import JWTError, jwt
from datetime import datetime, timedelta, UTC
from schemas import TokenData
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
import models, database
from sqlalchemy.orm import Session
from config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)

    return encoded_jwt

def verify_access_token(token: str, credentials_exeception):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id: str = payload.get("user_id")

        if id is None:
            raise credentials_exeception
        
        try:
            token_data = TokenData(id=str(id))
        except ValidationError as exc:
            print(repr(exc.errors()[0]['type']))
    except JWTError:
        raise credentials_exeception
    
    return token_data
    
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exeception = HTTPException(status.HTTP_401_UNAUTHORIZED,
                                           detail="Could not vaildate credentials", 
                                           headers={"WWW-Authenticate": "Bearer"})
    
    token = verify_access_token(token, credentials_exeception)
    user = db.query(models.User).filter(models.User.id == token.id).first()
    
    return user