from fastapi import FastAPI, APIRouter,status,HTTPException,Depends,Request, UploadFile, File, Form
from fastapi.responses import JSONResponse
# from database import database
from models import schemas
from bson import ObjectId
import json
from bson.errors import InvalidId
from auth.dependencies import get_authenticated_agent_db
from pymongo.errors import DuplicateKeyError
import os
from os.path import splitext
from functions.extract_text_from_pdf import extract_text_from_image,extract_text_from_pdf,send_to_llama,safe_parse_dict
import logging
from typing import Any, Dict
import re
import datetime
import tempfile
from cloudinary.exceptions import Error as CloudinaryError
from cloudinary.uploader import upload as cloudinary_upload
logger = logging.getLogger(__name__)
app = FastAPI()

router = APIRouter(
    prefix='/profile',
    tags=['Profile']
    )

UPLOAD_DIR = "uploads"  # Directory to store uploaded PDFs
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Create folder if not exists

# @router.post("/create-profile")
# async def create_profile( profile: schemas.ProfileCreate,user_db= Depends(get_authenticated_agent_db)):
#     try:
#         user, db = user_db  # Unpack user & database from function
#         previous_id = await db["user_profiles"].count_documents({})
#         biodata = {
#             "profile_id": previous_id+1,
#             "full_name": profile.full_name,
#             "age": profile.age,
#             "gender": profile.gender,
#             "marital_status": profile.marital_status,
#             "complexion": profile.complexion,
#             "height": profile.height,
#             "education": profile.education,
#             "maslak_sect": profile.maslak_sect,
#             "occupation": profile.occupation,
#             "native_place": profile.native_place,
#             "residence": profile.residence,
#             "siblings": profile.siblings,
#             "father_name": profile.father_name,
#             "mother_name": profile.mother_name,
#             'religious_practice': profile.religious_practice,
#             "contact_no": profile.contact_no,
#             "preferences": profile.preferences,
#             "pref_age_range": profile.pref_age_range,
#             "pref_marital_status": profile.pref_marital_status,
#             "pref_height": profile.pref_height,
#             "pref_complexion": profile.pref_complexion,
#             "pref_education": profile.pref_education,
#             "pref_work_job": profile.pref_work_job,
#             "pref_father_occupation": profile.pref_father_occupation,
#             "pref_no_of_siblings": profile.pref_no_of_siblings,
#             "pref_native_place": profile.pref_native_place,
#             "pref_mother_tongue": profile.pref_mother_tongue,
#             "pref_go_to_dargah": profile.pref_go_to_dargah,
#             "pref_maslak_sect": profile.pref_maslak_sect,
#             "pref_deendari": profile.pref_deendari,
#             "pref_location": profile.pref_location,
#             "created_at": datetime.datetime.now(datetime.timezone.utc)
#         }
        

#         if await db["user_profiles"].find_one({'full_name': biodata["full_name"]}):
#             return HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Profile already exists",
#             )
#         if await db["user_profiles"].find_one({'father_name': biodata["father_name"]}):
#             return HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Profile already exists",
#             )
#         if await db["user_profiles"].find_one({'contact_no': biodata["contact_no"]}):
#             return HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Profile already exists",
#             )
        
#         added = await db["user_profiles"].insert_one(biodata)
#         if not added.inserted_id:
#             raise HTTPException(status_code=500, detail="Failed to add profile to the database")
        
#         return JSONResponse(status_code=status.HTTP_200_OK, content={'message': 'Profile Created Successfully'})
        
#     except Exception as e:
#         print(f"Unexpected Error: {e}")  # Log the error
#         return HTTPException(status_code=500, detail="An unexpected error occurred")
    

@router.post("/create-profile")
async def create_profile(
    profile: str = Form(...),  # JSON string
    profile_image: UploadFile = File(None),
    user_db=Depends(get_authenticated_agent_db)
):
    try:
        # ✅ Parse JSON string to Pydantic model
        try:
            profile_data = schemas.ProfileCreate(**json.loads(profile))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid profile data: {e}")
        image_url = None
        if profile_image:
            # ✅ Upload image to Cloudinary
            try:
                result = cloudinary_upload(profile_image.file, folder="matrimony_profiles")
                image_url = result.get("secure_url")
                print(f"image_url {image_url}")
            except CloudinaryError as e:
                raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

        user, db = user_db
        previous_id = await db["user_profiles"].count_documents({})

        biodata = profile_data.model_dump()
        biodata.update({
            "profile_id": previous_id + 1,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        })
        
        if image_url:
            biodata["image_url"] = image_url

        # ✅ Duplicate checks
        for key in ["full_name", "father_name", "contact_no"]:
            if await db["user_profiles"].find_one({key: biodata[key]}):
                return HTTPException(status_code=400, detail=f"{key.replace('_', ' ').title()} already exists")

        added = await db["user_profiles"].insert_one(biodata)
        if not added.inserted_id:
            return HTTPException(status_code=500, detail="Failed to add profile to the database")

        return JSONResponse(status_code=200, content={'message': 'Profile Created Successfully'})

    except Exception as e:
        print(f"Unexpected Error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    

@router.get("/get-profile/{profile_id}")
async def get_profile(request: Request,profile_id: str,user_db=Depends(get_authenticated_agent_db)):
    user, db = user_db
    try:
        obj_id = ObjectId(profile_id)
    except InvalidId:
        return {"error": "Invalid ID"}
    profile = await db["user_profiles"].find_one({'_id': obj_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile not found",
        )
    
    profile["_id"] = str(profile["_id"])  # Fix ObjectId issue

    return JSONResponse(status_code=200, content={"profile":profile})

@router.put("/update-profile/{profile_id}")
async def update_profile(
    profile_id: str,
    update_data: schemas.UpdateProfileRequest,
    user_db=Depends(get_authenticated_agent_db)
):
    user, db = user_db

    # Validate ObjectId
    try:
        obj_id = ObjectId(profile_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid profile ID")

    # Convert Pydantic model to dict, skipping None fields
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}

    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Perform the update
    result = await db["user_profiles"].update_one(
        {"_id": obj_id},
        {"$set": update_dict}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Optional: Fetch updated profile to return
    updated_profile = await db["user_profiles"].find_one({"_id": obj_id})
    updated_profile["_id"] = str(updated_profile["_id"])

    return JSONResponse(status_code=200, content={
        "message": "Profile updated successfully",
        "profile": updated_profile
    })

@router.delete("/delete-profile/{profile_id}")
async def delete_profile(request: Request,profile_id: str,user_db=Depends(get_authenticated_agent_db)):
    user, db = user_db
    try:
        obj_id = ObjectId(profile_id)
    except InvalidId:
        return {"error": "Invalid ID"}
    profile = await db["user_profiles"].find_one_and_delete({'_id': obj_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile not found",
        )
    profile["_id"] = str(profile["_id"])  # Fix ObjectId issue
    return JSONResponse(status_code=200, content={"messeage": "profile deleted"})



# @router.get("/full-details")
# async def full_profile(profile_id: int, user_db = Depends(get_authenticated_agent_db)):
#     user, db = user_db
#     profile = await db["user_profiles"].find_one({"profile_id": profile_id})
#     if not profile:
#         return JSONResponse(status_code=404, content={"error": "Profile not found"})
#     # Convert ObjectId to str
#     profile["_id"] = str(profile["_id"])
#     print(profile)
#     return  JSONResponse(status_code=200, content={"profile": profile}) # FastAPI will return JSON
@router.get("/full-details")
async def full_profile(profile_id: str, user_db = Depends(get_authenticated_agent_db)):
    user, db = user_db
    try:
        obj_id = ObjectId(profile_id)
    except InvalidId:
        return {"error": "Invalid ID"}
    profile = await db["user_profiles"].find_one({'_id': obj_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile not found",
        )
    
    profile["_id"] = str(profile["_id"])  # Fix ObjectId issue

    return JSONResponse(status_code=200, content={"profile":profile})
    
    

@router.post("/upload-pdf")
async def upload_biodata(request: Request, file: UploadFile = File(...), user_db=Depends(get_authenticated_agent_db)):
    user, db = user_db
    result = None

    try:     
        # Save uploaded file temporarily
        filename = file.filename or "tempfile"
        suffix = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Determine if it's image or PDF
        if suffix.lower() == ".pdf":
            extracted_text = extract_text_from_pdf(tmp_path)
        else:
            extracted_text = extract_text_from_image(tmp_path)

        # Extract structured data from LLaMA via Groq API
        response_text = send_to_llama(extracted_text, api_key=os.getenv("GROQ_API_KEY"))
        profile_data = safe_parse_dict(response_text)
        profile_data["row_text"] = extracted_text

        print(f"profile-data: {profile_data}")
        # ✅ Duplicate checks
        for key in ["full_name", "father_name", "contact_no"]:
            if await db["user_profiles"].find_one({key: profile_data[key]}):
                raise HTTPException(status_code=400, detail=f"{key.replace('_', ' ').title()} already exists")
            
        # Insert into DB
        result = await db["user_profiles"].insert_one(profile_data)
        profile_id = str(result.inserted_id)[-6:].lower()
        await db["user_profiles"].update_one(
            {"_id": result.inserted_id},
            {"$set": {"profile_id": profile_id}}
        )

        return JSONResponse(status_code=200, content={
            "message": "Upload successful.",
            "profile_id": profile_id,
            "_id": str(result.inserted_id)
        })

    except DuplicateKeyError:
        if result:
            await db["user_profiles"].delete_one({"_id": result.inserted_id})
        raise HTTPException(status_code=409, detail="Duplicate profile ID.")
    except Exception as e:
        if result:
            await db["user_profiles"].delete_one({"_id": result.inserted_id})
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        # Clean up the temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    

# ------------------------------------------------------------------
# 1.  Minimal synonym dictionary (expand at will)
# ------------------------------------------------------------------
KEYWORDS: Dict[str, Dict[str, list[str]]] = {
    "gender": {
        "male":   ["male", "males", "man", "men"],
        "female": ["female", "females", "woman", "women"]
    },
    "native_place": {
        "hyderabad": ["hyderabad", "hyd"],
        "mumbai":    ["mumbai", "bombay", "bom"],
        "bangalore": ["bangalore", "bengaluru", "blr"],
        "delhi":     ["delhi", "new delhi"],
        "canada": ["canada","Canada"]
    },
    
    "education": {
    # MBBS / medical
    "mbbs":      ["mbbs", "m.b.b.s", "m b b s", "bachelor of medicine", "bachelor of medicine & surgery", "mbchb", "md", "doctor of medicine"],

    # engineering
    "b.e":       ["b.e", "be", "bachelor of engineering", "b.tech", "btech", "bachelor of technology", "m.e", "me", "m.tech", "mtech"],
    "b.tech":       ["bachelor of engineering", "b.tech", "btech", "bachelor of technology", "B.tech", "btech","B-tech"],

    # commerce
    "b.com":     ["b.com", "bcom", "bachelor of commerce", "m.com", "mcom", "master of commerce"],

    # science
    "b.sc":      ["b.sc", "bsc", "bachelor of science", "m.sc", "msc", "master of science"],

    # business administration
    "bba":       ["bba", "bachelor of business administration", "mba", "master of business administration"],

    # arts / humanities
    "ba":        ["ba", "b.a", "bachelor of arts", "m.a", "ma", "master of arts"],

    # pharmacy
    "b.pharm":   ["b.pharm", "bpharm", "bachelor of pharmacy"],

    # computer applications
    "bca":       ["bca", "bachelor of computer applications", "mca", "master of computer applications"],

    # diploma / polytechnic
    "diploma":   ["diploma", "polytechnic", "poly"]
},
"marital_status":{
        "single": ["Single", "single"],
        "Unmarried": ["Unmarried", "Unmarried"]
    },
}

STOP_WORDS = {"in", "from", "at", "a", "an", "the", "with", "degree", "all", "and", "of"}

def build_mongo_filter(query: str) -> Dict[str, Any]:
    query = query.lower()
    tokens = [w for w in re.split(r"[,\s]+", query) if w and w not in STOP_WORDS]

    filt: Dict[str, Any] = {}

    # 1.  map recognised tokens to exact/regex filters
    for tok in tokens:
        for field, mapping in KEYWORDS.items():
            for canonical, aliases in mapping.items():
                if tok in aliases:
                    if field in ("gender", "native_place"):
                        filt[field] = {"$regex": f"^{re.escape(canonical)}$", "$options": "i"}
                    else:
                        alias_pattern = "|".join(map(re.escape, aliases))
                        filt[field] = {"$regex": alias_pattern, "$options": "i"}
                        break
                


    # 2.  handle free terms (age, education, etc.) the same way
    #     skip gender & location – they were already handled
    free = [t for t in tokens if t not in {
        alias
        for m in KEYWORDS.values()
        for lst in m.values()
        for alias in lst
    }]
    if free:
        ors = []
        for f in free:
            ors.extend([
                {"education": {"$regex": f"\\b{re.escape(f)}\\b", "$options": "i"}},
                {"residence":    {"$regex": f"\\b{re.escape(f)}\\b", "$options": "i"}},
                {"age": {"$regex": f"^{re.escape(f)}$", "$options": "i"}} if f.isdigit() else {}
            ])
        ors = [o for o in ors if o]
        if ors:
            filt["$or"] = ors

    return filt

@router.get("/search")
async def search_profiles(
    query: str,
    page: int = 1,
    db=Depends(get_authenticated_agent_db)
):
    try:
        user, db = db
        limit = 6
        skip_ = (page - 1) * limit
        
        # cursor = db["user_profiles"].find(
        #     { "$text": { "$search": query } },
        #     { "score": { "$meta": "textScore" } }
        # ).sort([("score", { "$meta": "textScore" })]).skip(skip).limit(limit)
        
        filter_dict = build_mongo_filter(query)
        print(filter_dict)
        cursor = (
            db["user_profiles"]
            .find(filter_dict)          # include _id by default
            .skip(skip_)
            .limit(limit)
        )

        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        print(f'count: {len(results)}, results: {results}')
        return {"results": results}
    except Exception as e:
        print(f"Unexpected Error: {e}")  # Log the error
        raise HTTPException(status_code=500, detail="An unexpected error occurred")