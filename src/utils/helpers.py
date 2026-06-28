from sqlalchemy.orm import Session
from src.auth.model import UserModel
from fastapi import HTTPException, status, Request, Depends
import jwt
from src.utils.settings import settings
from jwt.exceptions import InvalidTokenError
from src.utils.db import get_db

from fastapi.security import  APIKeyHeader, HTTPBearer
from fastapi import Form

api_key_header = APIKeyHeader(name="Authorization")
# bearer = HTTPBearer()

def is_authenticated(token: str = Depends(api_key_header), db:Session = Depends(get_db)):
    try:
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
        
        token  = token.split(" ")[-1]

        data = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        user_id = data.get("_id")
        
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

        return user
    
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")



# def is_authenticated(request: Request, db:Session = Depends(get_db)):
#     try:
#         token = request.headers.get("authorization")
