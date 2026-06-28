from fastapi import APIRouter, Form, Depends, status, Request
from sqlalchemy.orm import Session
from src.utils.db import get_db
from src.auth.dtos import UserSchema, UserResponseSchema, LoginSchema, TokenResponse
from src.auth import controller
from src.utils.helpers import is_authenticated

auth_routes = APIRouter(prefix="/auth")


@auth_routes.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED,
                    responses={409: {"description": "Conflict Error"}}
                  )
def register(body: UserSchema, db: Session = Depends(get_db)):
    return controller.register(body, db)



@auth_routes.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK, 
                    responses={401: {"description": "Authorization Error"}}
                  )
def login(body: LoginSchema, db: Session = Depends(get_db)):

    return controller.login(body, db)

@auth_routes.get("/is_auth", response_model=UserResponseSchema, status_code=status.HTTP_200_OK,
                    responses={401: {"description": "Authorization Error"}}
                )
def is_auth(user: UserSchema = Depends(is_authenticated)):
    return user
