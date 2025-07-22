from fastapi import FastAPI, APIRouter,status,HTTPException,Depends
from fastapi.responses import JSONResponse, Response
from auth.dependencies import admin_required
from typing import Optional, List
from models.schemas import UserInfo
from database import database

# load_dotenv()
app = FastAPI()

router = APIRouter(prefix='/admin', tags=['Admin'])

async def approve_user_in_db(username: str) -> Optional[UserInfo]:
    user = await database.agents_collection.find_one({"username": username})

    if not user:
        return None

    # Update status to 'approved'
    await database.agents_collection.update_one(
        {"username": username},
        {"$set": {"status": "approved"}}
    )

    # Fetch updated user
    updated_user = await database.agents_collection.find_one({"username": username})
    if not updated_user:
        return None  # 👈 Prevent crash if update failed

    return UserInfo(
        agent_id=str(updated_user["_id"]),
        username=updated_user.get("username", ""),
        email=updated_user.get("email", ""),
        status=updated_user.get("status", ""),
        role=updated_user.get("role", "")
    )

async def disapprove_user_in_db(username: str) -> Optional[UserInfo]:
    user = await database.agents_collection.find_one({"username": username})

    if not user:
        return None

    # Update status to 'approved'
    await database.agents_collection.update_one(
        {"username": username},
        {"$set": {"status": "pending"}}
    )

    # Fetch updated user
    updated_user = await database.agents_collection.find_one({"username": username})
    if not updated_user:
        return None  # 👈 Prevent crash if update failed

    return UserInfo(
        agent_id=str(updated_user["_id"]),
        username=updated_user.get("username", ""),
        email=updated_user.get("email", ""),
        status=updated_user.get("status", ""),
        role=updated_user.get("role", "")
    )


@router.get("/dashboard", response_model=List[UserInfo])
async def admin_dashboard(admin: dict = Depends(admin_required)):
    """
    Endpoint to list all users in the system.
    Only accessible by administrators.
    """
    print(f"Admin '{admin['agent_username']}' is accessing the user list.")
    
    # Replace with your actual MongoDB collection
    users_cursor = database.agents_collection.find()  # e.g., db["users"]
    users = await users_cursor.to_list(length=None)

    # Convert MongoDB documents to Pydantic model
    user_list = [
        UserInfo(
            agent_id=str(user.get("_id", "")),
            username=user.get("username", ""),
            email=user.get("email", ""),
            status=user.get("status", ""),
            role=user.get("role", "")
        )
        for user in users
        if user.get("role", "") == "user"
    ]

    return user_list

@router.get("/users", response_model=List[UserInfo])
async def list_users_for_admin(admin: dict = Depends(admin_required)):
    """
    Endpoint to list all users in the system.
    Only accessible by administrators.
    """
    print(f"Admin '{admin['agent_username']}' is accessing the user list.")
    
    # Replace with your actual MongoDB collection
    users_cursor = database.agents_collection.find()  # e.g., db["users"]
    users = await users_cursor.to_list(length=None)

    # Convert MongoDB documents to Pydantic model
    user_list = [
        UserInfo(
            agent_id=str(user.get("_id", "")),
            username=user.get("username", ""),
            email=user.get("email", ""),
            status=user.get("status", ""),
            role=user.get("role", "")
        )
        for user in users
        if user.get("role", "") == "user"
    ]

    return user_list


@router.patch("/users/{username}/approve", response_model=UserInfo)
async def approve_user_registration(username: str, admin= Depends(admin_required)):
    """
    Endpoint for an admin to approve a user's registration.
    Sets the `is_approved` flag to True for the specified user.
    """
    print(f"Admin '{admin['agent_username']}' is attempting to approve user '{username}'.")
    approved_user = await approve_user_in_db(username)
    if not approved_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found."
        )
    
    # try:
    #     db = database.client[f"{username}_matrimony"]
    #     collection = db["user_profiles"]
    #     # Fix invalid language values
    #     await collection.update_many(
    #         { "language": { "$exists": True } },
    #         { "$set": { "language": "english" } }
    #     )

    #     # Create text index on key fields
    #     await collection.create_index(
    #         {
    #             "full_name": "text",
    #             "education": "text",
    #             "gender": "text",
    #             "marital_status": "text",
    #             "height": "text",
    #             "age": "text",
    #             "preferences": "text"
    #         },
    #         name="TextSearchIndex",
    #         default_language="english"
    #     )

    #     print(f"✅ Index created and language cleaned for user DB: {db}")

    # except Exception as e:
    #     print(f"❌ Index setup failed for user '{username}': {e}")
    return JSONResponse(status_code=200,content={"message": "User Approved Successfully"})

@router.patch("/users/{username}/disapprove", response_model=UserInfo)
async def disapprove_user_registration(username: str, admin= Depends(admin_required)):
    """
    Endpoint for an admin to approve a user's registration.
    Sets the `is_approved` flag to True for the specified user.
    """
    print(f"Admin '{admin['agent_username']}' is attempting to disapprove user '{username}'.")
    disapproved_user = await disapprove_user_in_db(username)
    if not disapproved_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found."
        )
    
    # try:
    #     db = database.client[f"{username}_matrimony"]
    #     collection = db["user_profiles"]
    #     # Fix invalid language values
    #     await collection.update_many(
    #         { "language": { "$exists": True } },
    #         { "$set": { "language": "english" } }
    #     )

    #     # Create text index on key fields
    #     await collection.create_index(
    #         {
    #             "full_name": "text",
    #             "education": "text",
    #             "gender": "text",
    #             "marital_status": "text",
    #             "height": "text",
    #             "age": "text",
    #             "preferences": "text"
    #         },
    #         name="TextSearchIndex",
    #         default_language="english"
    #     )

    #     print(f"✅ Index created and language cleaned for user DB: {db}")

    # except Exception as e:
    #     print(f"❌ Index setup failed for user '{username}': {e}")
    return JSONResponse(status_code=200,content={"message": "User Approved Successfully"})