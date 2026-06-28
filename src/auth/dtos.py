from pydantic import BaseModel, field_validator
import re

class UserSchema(BaseModel):
    name: str 
    username: str 
    password: str
    email: str

    @field_validator("password")
    def password_strength(cls, v: str) -> str:
        regex = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'
        if not re.match(regex, v):
            raise ValueError(
                "Password must contain uppercase, lowercase, digit, special char, and be 8+ chars long"
            )
        return v

class UserResponseSchema(BaseModel):
    id: int
    name: str 
    username: str 
    email: str

class LoginSchema(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    token: str