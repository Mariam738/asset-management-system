from src.auth.dtos import UserSchema, LoginSchema, TokenResponse
from sqlalchemy.orm import Session
from src.auth.model import UserModel
from fastapi import HTTPException, status, Request
from pwdlib import PasswordHash
import jwt
from src.utils.settings import settings
from datetime import datetime, timedelta
from jwt.exceptions import InvalidTokenError

password_hash = PasswordHash.recommended()

def get_password_hash(password):
    return password_hash.hash(password)

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def register(body: UserSchema, db: Session):
    is_user = db.query(UserModel).filter(UserModel.username == body.username).first()
    if is_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    is_user = db.query(UserModel).filter(UserModel.email == body.email).first()
    if is_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    hash_password = get_password_hash(body.password)
    data = body.model_dump()
    data["hash_password"] = hash_password
    data.pop("password")
    user = UserModel(**data)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def login(body: LoginSchema, db: Session):
    user = db.query(UserModel).filter(UserModel.email == body.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")

    if not verify_password(body.password, user.hash_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")

    exp_time = datetime.now() + timedelta(minutes=settings.EXP_MINUTES)
    
    token = jwt.encode({"_id": user.id, "exp": exp_time.timestamp()}, settings.SECRET_KEY, settings.ALGORITHM)

    return TokenResponse(token= token)


