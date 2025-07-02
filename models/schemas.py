from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="User's unique username")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password")
    
class UserPublic(BaseModel):
    id: str
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class ProfileCreate(BaseModel):
    full_name: str
    age: int
    date_of_birth: Optional[str] = None
    gender: str
    marital_status: str
    complexion: str
    height: str
    education: str 
    maslak_sect: str
    occupation: str
    native_place: Optional[str] = None
    residence: str
    siblings: Optional[str] = None
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    religious_practice: str
    preferences: str
    pref_age_range: str
    pref_marital_status: str
    pref_height: str
    pref_complexion: str
    pref_education: str
    pref_work_job: Optional[str] = None
    pref_father_occupation: Optional[str] = None
    pref_no_of_siblings: Optional[str] = None
    pref_native_place: str
    pref_mother_tongue: str
    pref_go_to_dargah: Optional[str] = None
    pref_maslak_sect:str
    pref_deendari: str
    pref_location: str