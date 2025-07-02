from fastapi import FastAPI, APIRouter,status,HTTPException,Depends
from fastapi.responses import JSONResponse
from database import database
from models import schemas
from auth.dependencies import get_authenticated_agent_db

app = FastAPI()

router = APIRouter(
    prefix='/profile',
    tags=['Profile']
    )

@router.post("/create-profile")
async def create_profile( profile : schemas.ProfileCreate,user_db= Depends(get_authenticated_agent_db)):
    try:
        user, db = user_db  # Unpack user & database from function
        previous_id = await db["user_profiles"].count_documents({})
        biodata = {
            "profile_id": previous_id+1,
            "full_name": profile.full_name,
            "age": profile.age,
            "gender": profile.gender,
            "marital_status": profile.marital_status,
            "complexion": profile.complexion,
            "height": profile.height,
            "education": profile.education,
            "maslak_sect": profile.maslak_sect,
            "occupation": profile.occupation,
            "native_place": profile.native_place,
            "residence": profile.residence,
            "siblings": profile.siblings,
            "father": profile.father_name,
            "mother": profile.mother_name,
            'religious_practice': profile.religious_practice,
            "preferences": profile.preferences,
            "pref_age_range": profile.pref_age_range,
            "pref_marital_status": profile.pref_marital_status,
            "pref_height": profile.pref_height,
            "pref_complexion": profile.pref_complexion,
            "pref_education": profile.pref_education,
            "pref_work_job": profile.pref_work_job,
            "pref_father_occupation": profile.pref_father_occupation,
            "pref_no_of_siblings": profile.pref_no_of_siblings,
            "pref_native_place": profile.pref_native_place,
            "pref_mother_tongue": profile.pref_mother_tongue,
            "pref_go_to_dargah": profile.pref_go_to_dargah,
            "pref_maslak_sect": profile.pref_maslak_sect,
            "pref_deendari": profile.pref_deendari,
            "pref_location": profile.pref_location
        }
        
        added = await db["user_profiles"].insert_one(biodata)
        if not added.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to add profile to the database")
        
        return JSONResponse(status_code=status.HTTP_200_OK, content={'message': 'Profile Created Successfully'})
        
    except Exception as e:
        print(f"Unexpected Error: {e}")  # Log the error
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    

# @router.get("/get-profile")
# def get_profile()
    
