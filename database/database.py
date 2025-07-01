from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
# connect = MongoClient(MONGO_URI)
client = AsyncIOMotorClient(MONGO_URI)
agents_db = client["matrimony_agents"] # Common DB for storing agents

agents_collection = agents_db['agents']

def agent_helper(agent) -> dict:
    return {
        "id": str(agent["_id"]),
        "username": agent["username"],
        "email": agent["email"],
        "full_name": agent.get("full_name"),
    }