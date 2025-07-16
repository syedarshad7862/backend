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
import time
load_dotenv()
app = FastAPI()
router = APIRouter(prefix='/match', tags=['Match'])
MONGO_URI = os.getenv("MONGO_URI")
# MONGO_URI = "mongodb://localhost:27017/"

@router.get("/find")
async def find_matches(request: Request,user_db=Depends(get_authenticated_agent_db)):
    try:
        user, db = user_db
        profiles = await db["user_profiles"].find({}, {"_id": 1, "full_name": 1, "profile_id": 1}).to_list(length=None)
        # profiles = await db["user_profiles"].find({}).limit(50).to_list(length=50)
        for profile in profiles:
            profile['_id'] = str(profile['_id'])
    
        return JSONResponse(status_code=status.HTTP_200_OK, content={"profiles": profiles})
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
    start_time = time.time()
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
        full_name = selected_profile.get("full_name", "full_name")
        print(f"profile_id and full_name: {profile_id}, {full_name}")
        chunk_start = time.time()
        # function for dataframe & chunks
        texts ,profile_df = await chunks.create_chunks(MONGO_URI,db.name,"user_profiles")
        print(f"Time to create chunks: {time.time() - chunk_start:.2f} sec")
        
        # print(profile_df)
        # pdb.set_trace()
        vector_start = time.time()
        matched_profiles, query_text = search_vector.extract_indices_from_vector(profile_df,profile_id,full_name,profile.top)
        print(f"Time for vectors search: {time.time() - vector_start:.2f} sec")
        if matched_profiles.empty:
            print("No Matches found!")
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "No Matches Found!"})
        llm_start = time.time()
        llm_response = match_making.semantic_search_llm(matched_profiles, query_text)
        print(f"Time for LLM semantic search: {time.time() - llm_start:.2f} sec")
        print(f"print from llm response: {llm_response}")
        response_start = time.time()  
        result = structure_output.transform_llm_response(llm_response)
        print(f"Time for transform llm response {time.time() - response_start:.2f} sec")
        # selected_profile['_id'] = str(selected_profile["_id"])
        matches = [m.dict() for m in result['matches']]
        total_time = time.time() - start_time  # ⏱️ End timing
        print(f"Total execution time: {total_time:.2f} seconds")
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