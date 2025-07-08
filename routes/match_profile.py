from fastapi import FastAPI, APIRouter,status,HTTPException,Depends,Request
from fastapi.responses import JSONResponse
from auth.dependencies import get_authenticated_agent_db
from models import schemas
from bson import ObjectId
from bson.errors import InvalidId
from functions.generate_vectors import create_faiss_index
from functions import chunks,search_vector,match_making,structure_output
import os
from dotenv import load_dotenv
import pdb
load_dotenv()
app = FastAPI()
router = APIRouter(prefix='/match', tags=['Match'])
MONGO_URI = os.getenv("MONGO_URI")
# MONGO_URI = "mongodb://localhost:27017/"

@router.get("/find")
async def find_matches(request: Request,user_db=Depends(get_authenticated_agent_db)):
    try:
        user, db = user_db
        profiles = await db["user_profiles"].find({}).to_list(length=None)
        for profile in profiles:
            profile['_id'] = str(profile['_id'])
    
        return JSONResponse(status_code=status.HTTP_302_FOUND, content={"profiles": profiles})
    except Exception as e:
        print(f"Error logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profiles not available.",
        )
    
@router.post("/show-matches")
async def show_matches(
    request: Request,
    profile: schemas.SelectProfile,
    user_db=Depends(get_authenticated_agent_db)
):
    try:
        user, db = user_db
        try:
            obj_id = ObjectId(profile.profile_id)
        except InvalidId:
            return {"error": "Invalid ID"}
        print(profile)
        # Find the selected user profile
        selected_profile = await db["user_profiles"].find_one({"_id": obj_id})
        print(f"database url: {MONGO_URI} user: {user}")
        if not selected_profile:
            return JSONResponse(status_code=404, content={"error": "Profile not found"})
        profile_id = selected_profile.get("profile_id", "profile_id")
        print(f"full_name: {profile_id}")
        # function for dataframe & chunks
        texts ,profile_df = await chunks.create_chunks(MONGO_URI,db.name,"user_profiles")
        
        # print(profile_df)
        # pdb.set_trace()
        matched_profiles, query_text = search_vector.extract_indices_from_vector(profile_df,profile_id,profile.top)
        if matched_profiles.empty:
            print("No Matches found!")
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "No Matches Found!"})
        
        llm_response = match_making.semantic_search_llm(matched_profiles, query_text)
        print(f"print from llm response: {llm_response}")
            
        result = structure_output.transform_llm_response(llm_response)
        # selected_profile['_id'] = str(selected_profile["_id"])
        matches = [m.dict() for m in result['matches']]
        print(matches)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"matche_profiles": matches})
    except Exception as e:
        print(f"Error logs: {e}")
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal servet error",
            )
    
@router.post("/create-vectors")
async def generate_vectors(request: Request, user_db= Depends(get_authenticated_agent_db)):
    user, db = user_db
    print(f"database url: {MONGO_URI} user: {user}")
    await create_faiss_index(MONGO_URI,db.name,"user_profiles")
    # print(MONGO_URI,db.name,"user_profiles")
    return {"message": "Created vectors successfully!"}