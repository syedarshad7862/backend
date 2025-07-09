from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="User's unique username")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password")
    role: str = "user" # default role user
    status: str = "pending"
class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="User's unique username")
    password: str = Field(..., min_length=8,description="User's password")
    
class UserPublic(BaseModel):
    id: str
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserInfo(BaseModel):
    """User data that is safe to be sent to clients."""
    agent_id: str
    username: str
    email: EmailStr
    role: str
    status: str

class Token(BaseModel):
    access_token: str
    token_type: str
class SelectProfile(BaseModel):
    profile_id: str
    top: int
    
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
    

class UpdateProfileRequest(BaseModel):
    full_name: str | None = None
    age: int | None = None
    date_of_birth: str | None = None
    gender: str | None = None
    marital_status: str  | None = None
    complexion: str | None = None
    height: str | None = None
    education: str  | None = None
    maslak_sect: str | None = None
    occupation: str | None = None
    native_place: str | None = None
    residence: str | None = None
    siblings: str | None = None
    father_name: str | None = None
    mother_name: str | None = None
    religious_practice: str | None = None
    preferences: str | None = None
    pref_age_range: str | None = None
    pref_marital_status: str | None = None
    pref_height: str | None = None
    pref_complexion: str | None = None
    pref_education: str | None = None
    pref_work_job: str | None = None
    pref_father_occupation: str | None = None
    pref_no_of_siblings: str | None = None
    pref_native_place: str | None = None
    pref_mother_tongue: str | None = None
    pref_go_to_dargah: str | None = None
    pref_maslak_sect:str | None = None
    pref_deendari: str | None = None
    pref_location: str | None = None