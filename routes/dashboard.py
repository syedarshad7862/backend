from fastapi import FastAPI, APIRouter,status,HTTPException,Depends
from fastapi.responses import JSONResponse
from database import database
from auth.dependencies import get_authenticated_agent_db

app = FastAPI()

router = APIRouter(
    prefix='/dashboard',
    tags=['Dashboard'],
    dependencies=[Depends(get_authenticated_agent_db)] 
    )


@router.get("/dashboard")
async def get_dashboard_data(user_db= Depends(get_authenticated_agent_db)):
    user, db = user_db  # Unpack user & database from function
    total_profiles = await db["user_profiles"].count_documents({})
    
    # Count male users
    total_male = await db["user_profiles"].count_documents({"gender": "Male"})

    # Count female users
    total_female = await db["user_profiles"].count_documents({"gender": "Female"})
    return JSONResponse(status_code=status.HTTP_200_OK, content={'total_profiles': total_profiles,'total_male': total_male, 'total_female': total_female})