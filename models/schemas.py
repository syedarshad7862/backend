from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=50, description="User's unique username")
    password: str = Field(..., min_length=8, description="User's password")
    
class UserPublic(BaseModel):
    id: str
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    
class Token(BaseModel):
    access_token: str
    token_type: str