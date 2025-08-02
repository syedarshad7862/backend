import pandas as pd
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import os

load_dotenv()

# # Function to normalize embeddings
# def normalize_embeddings(embeddings):
#     return embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

# def extract_indices_from_vector(df, profile_id,full_name,top_k):
    
#     # Get user profile
#     user_profile = df[(df["profile_id"] == profile_id) & (df["full_name"] == full_name)]
#     if user_profile.empty:
#         return pd.DataFrame(), "❌ User not found."
#     print(f"username find in {user_profile}")
#     user_gender = user_profile.iloc[0]["gender"]

#     model = SentenceTransformer("all-MiniLM-L6-v2")
    
#     # Select the appropriate FAISS index
#     if user_gender == "Male":
#         matched_df = df[df["gender"] == "Female"]  # Male searches for females
#         index_path = r"C:\Users\ThinkPad\Desktop\python projects\backend\newvectorstore\female_index.faiss"  # Male users search in the female index
#         opposite_gender = "Female"
#     elif user_gender== "Female":
#         matched_df = df[df["gender"] == "Male"]  # Female searches for males
#         index_path = r"C:\Users\ThinkPad\Desktop\python projects\backend\newvectorstore\male_index.faiss"  # Female users search in the male index
#         opposite_gender = "Male"
#     else:
#         return pd.DataFrame(), "❌ Invalid gender."

#     print(f"🔍 User Gender: {user_gender}, Searching in: {index_path} (Looking for {opposite_gender})")

#     # Load the FAISS index
#     try:
#         index = faiss.read_index(index_path)
#     except Exception as e:
#         return pd.DataFrame(), f"❌ Error loading FAISS index: {str(e)}"

#     # Encode user profile text
#     query_text = user_profile.iloc[0]["text"]
#     query_embedding = model.encode([query_text]).astype("float32")
#     query_embedding = normalize_embeddings(query_embedding)

#     # Search FAISS
#     distance, faiss_indices = index.search(query_embedding, k=top_k)  # Retrieve extra for filtering
#     print(f"FAISS Retrieved Indices: {faiss_indices} and distances: {distance}")
    
#     matched_profiles = matched_df.iloc[faiss_indices[0]]  # Ensure only opposite gender profiles are retrieved

#     matched_profiles = matched_profiles.head(top_k)  # Return top-k results
#     print(f" from search function: {matched_profiles}")
#     if matched_profiles.empty:
#         return pd.DataFrame(), "❌ No matches found."
    
#     return matched_profiles, query_text



from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
import pandas as pd

# Search function using Qdrant
# async def qdrant_search_profiles(mongodb_uri, db_name, collection_name, profile_id, full_name, k=3):
#     from motor.motor_asyncio import AsyncIOMotorClient

#     # Connect to MongoDB
#     client = AsyncIOMotorClient(mongodb_uri)
#     db = client[db_name]
#     collection = db[collection_name]

#     # Find user profile
#     user_profile = await collection.find_one({
#         "profile_id": profile_id,
#         "full_name": full_name
#     })

#     if not user_profile:
#         return [], "❌ Profile not found."

#     user_gender = user_profile.get("gender")
#     if user_gender not in ["Male", "Female"]:
#         return [], "❌ Invalid gender."

#     # Opposite gender collection
#     collection_to_search = "female_profiles" if user_gender == "Male" else "male_profiles"

#     # Qdrant and embeddings setup
#     qdrant_url = "https://<your-cluster>.qdrant.cloud"
#     qdrant_api_key = "<your-api-key>"
#     embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
#     qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

#     # Create LangChain Qdrant wrapper
#     vectorstore = Qdrant(
#         client=qdrant_client,
#         collection_name=collection_to_search,
#         embeddings=embedding_model,
#     )

#     # Prepare the search query text (same as what you used during indexing)
#     profile_text = (
#         str(user_profile.get("profile_id", "")) + " \n" +
#         str(user_profile.get("full_name", "")) + " \n" +
#         "Age: " + str(user_profile.get("age", "")) + " \n" +
#         "Education: " + str(user_profile.get("education", "")) + " \n" +
#         "Location: " + str(user_profile.get("location", "")) + " \n" +
#         "Preferences: " + str(user_profile.get("preferences", ""))
#     )

#     # Perform similarity search
#     results = vectorstore.similarity_search(profile_text, k=k)
#     matched_profiles = [doc.page_content for doc in results]

#     if not matched_profiles:
#         return [], "❌ No similar profiles found."

#     return matched_profiles, "✅ Search complete."



# Search function using Qdrant
async def qdrant_search_profiles(df, profile_id,full_name, k=3):
		
	    # Get user profile
    user_profile = df[(df["profile_id"] == profile_id) & (df["full_name"] == full_name)]
    query_text = user_profile.iloc[0]["text"]
    
    if user_profile.empty:
        return pd.DataFrame(), "❌ User not found."
    print(f"username find in {user_profile}")
    user_gender = user_profile.iloc[0]["gender"]

    # Opposite gender collection
    # collection_to_search = "female_profiles" if user_gender == "Male" else "male_profiles"

	# Opposite gender collection
    if user_gender == "Male":
        matched_df = df[df["gender"] == "Female"]  # Male searches for females
        collection_to_search = "female_profiles"  # Male users search in the female index
        opposite_gender = "Female"
    elif user_gender== "Female":
        matched_df = df[df["gender"] == "Male"]  # Female searches for males
        collection_to_search = "male_profiles"  # Female users search in the male index
        opposite_gender = "Male"
    else:
        return pd.DataFrame(), "❌ Invalid gender."

    # Qdrant and embeddings setup
    qdrant_url = os.getenv("Qdrant_URL")
    qdrant_api_key = os.getenv("Qdrant_API_KEY")
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

    # Create LangChain Qdrant wrapper
    vectorstore = Qdrant(
        client=qdrant_client,
        collection_name=collection_to_search,
        embeddings=embedding_model,
    )
    

    # Perform similarity search
    results = vectorstore.similarity_search(query_text, k=k)
    # print(f"result of v {results} dir: {dir(results)}")
    # matched_profiles = [doc.page_content for doc in results]
    matched_profiles = [{
    "page_content": doc.page_content,
    "_id": doc.metadata.get("_id"),
    "profile_id": doc.metadata.get("profile_id"),
    "full_name": doc.metadata.get("full_name"),
    "gender": doc.metadata.get("gender")
    } for doc in results]

    # df_matched_profiles = pd.DataFrame(matched_profiles)



    df_matched_profiles = pd.DataFrame(matched_profiles)

    print(f"result from qdrant db {df_matched_profiles}")
    # print(matched_df.columns.tolist())
    # print(matched_df["_id"])
    if not matched_profiles:
        return [], "❌ No similar profiles found."

    # filter matche_df using _id values from qdrant search
    matched_id = df_matched_profiles['profile_id'].tolist()
    # print(matched_id)
    filtered_profiles = matched_df[matched_df["_id"].astype(str).isin(matched_id)]
    return filtered_profiles, query_text


