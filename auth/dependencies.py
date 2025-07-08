from fastapi import Request, HTTPException,status, Depends
# import jwt 
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta,timezone
from typing import Optional
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
load_dotenv()


SECRET_KEY = 'matrimonial-meer-ahmed-sir'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

MONGO_URI = os.getenv("MONGO_URI")
# print(MONGO_URI)
# connect = MongoClient(MONGO_URI)
client = AsyncIOMotorClient(MONGO_URI)
agents_db = client["matrimony_agents"] # Common DB for storing agents

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login",scheme_name="Bearer Authentication") # "token" is the endpoint where clients can get a token

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})  # 🔄 Expiration claim
    return jwt.encode(to_encode,SECRET_KEY, algorithm=ALGORITHM)  # 🔑 Encode JWT



# def get_authenticated_agent_db(request: Request):
#     token = request.cookies.get("access_token")

#     if not token:
#         raise HTTPException(status_code=401, detail="Not authenticated")

#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
#         agent_id = payload["agent_id"]
#         agent_username = payload["agent_username"].lower()  # Always use lowercase to avoid case issues
#         user = {"agent_id": agent_id, "agent_username": agent_username, "email": payload["email"]}
#         agent_db = client[f"matrimony_{agent_username}_{agent_id}"]
#         return user, agent_db # ✅ Return agent's DB
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Token expired")
#     except jwt.InvalidTokenError:
#         raise HTTPException(status_code=401, detail="Invalid token")


async def get_authenticated_agent_db(request: Request):
    """
    Dependency to get the current authenticated agent's user data and their specific database.
    Decodes the JWT token to get agent information, and constructs the agent's database reference.
    """
    
    token = request.cookies.get("accessToken") or \
            request.headers.get("Authorization", "").replace("Bearer ", "")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract specific claims for your agent
        agent_id: Optional[str] = payload.get("agent_id")
        agent_username: Optional[str] = payload.get("agent_username")
        email: Optional[str] = payload.get("email")

        if agent_id is None or agent_username is None or email is None:
            raise credentials_exception
            
        # Ensure agent_username is lowercase for consistent database naming
        agent_username = agent_username.lower()

        # You might want to validate if the user exists in a central user store
        # before proceeding to construct their specific database connection.
        # This is where `crud.get_user_by_username` or similar would fit.
        # For this specific conversion, we're directly using the payload.
        # If you need to verify the user against a central user database
        # based on the `agent_username` or `agent_id` from the token, you'd do it here:
        #
        # user_from_db = await crud.get_user_by_username(agent_username)
        # if user_from_db is None:
        #     raise credentials_exception
        # user_data = UserInDB(**user_from_db)

        # Construct the user data as your 'user' dictionary/object
        user_data = {"agent_id": agent_id, "agent_username": agent_username, "email": email}

        # Construct the agent's specific database reference
        # agent_db = client[f"matrimony_{agent_username}_{agent_id}"]
        agent_db = client[f"{agent_username}_matrimony"]
        
        return user_data, agent_db
    except JWTError as e:
        # This catches various JWT errors like ExpiredSignatureError, InvalidTokenError, etc.
        # The `detail` message can be more specific if you catch individual exceptions
        # as in your original function, but `JWTError` is a good catch-all for invalid tokens.
        print(f"JWT Error: {e}") # Log the specific error for debugging
        raise credentials_exception
    except Exception as e:
        # Catch any other unexpected errors during the process
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred during authentication."
        )

# --- Example Usage in a FastAPI Path Operation ---
# from fastapi import FastAPI
# app = FastAPI()

# @app.get("/protected-route")
# async def read_protected_data(
#     authenticated_agent_info: tuple[UserInDB, Any] = Depends(get_authenticated_agent_db)
# ):
#     user, agent_db = authenticated_agent_info
#     # Now you have the user's details and their specific database connection
#     # You can use agent_db to perform operations specific to this agent.
#     return {
#         "message": f"Welcome, {user.agent_username}! Accessing your database.",
#         "agent_id": user.agent_id,
#         "agent_email": user.email,
#         "agent_db_info": str(agent_db) # For demonstration, convert to string
#     }
