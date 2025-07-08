from fastapi import FastAPI, APIRouter,status,HTTPException,Depends
from fastapi.responses import JSONResponse, Response
from models import schemas
from database import database
from auth.jwt_utils import hash_password,verify_password
from auth.dependencies import create_access_token
from fastapi.security import OAuth2PasswordRequestForm
import datetime
import os
from dotenv import load_dotenv
load_dotenv()
app = FastAPI()

MONGO_URI = os.getenv("MONGO_URI")
router = APIRouter(prefix='/auth', tags=['Auth'])

@router.post("/register",response_model=schemas.UserPublic, status_code=status.HTTP_201_CREATED)
async def get_register(user: schemas.UserCreate):
    
    agent_data = {
    "username": user.username,
    "email": user.email,
    "password": hash_password(user.password),
    "created_at": datetime.datetime.now(datetime.timezone.utc)
    }
    print(MONGO_URI)
    if await database.agents_collection.find_one({'username':agent_data["username"]}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    if await database.agents_collection.find_one({'email':agent_data['email']}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    new_agent = await database.agents_collection.insert_one(agent_data)
    return JSONResponse(status_code=200, content={'message': 'User Created Successfully.'})

# OAuth2PasswordRequestForm = Depends()
@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(response: Response,form_data: schemas.UserLogin):
    """
    Handles user login. Verifies credentials and returns a JWT access token.
    FastAPI's OAuth2PasswordRequestForm expects form data, not JSON.
        """   
    # print(form_data.username)
    db_agents = await database.agents_collection.find_one({'username': form_data.username})
    if not db_agents or not verify_password(form_data.password, db_agents["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(data={"agent_id": str(db_agents["_id"]),"agent_username":str(db_agents["username"]), "email": db_agents["email"]})
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True,samesite='lax')
    return {"access_token": access_token, "token_type": "bearer"}



@router.post("/logout")
async def logout_agent(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}

    

# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhZ2VudF9pZCI6IjY4NjMwYzc5MjI4MTJiMWE5ODUzYTZlZSIsImFnZW50X3VzZXJuYW1lIjoiYXJzaGFkIiwiZW1haWwiOiJhcnNoYWRAZ21haWwuY29tIiwiZXhwIjoxNzUxMzI2MjY4fQ.FXz_pZPmCME91eDYWLporatGRXo1QlmQAWBuXKQiCaM