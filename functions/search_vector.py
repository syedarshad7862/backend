import pandas as pd
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

load_dotenv()

# Function to normalize embeddings
def normalize_embeddings(embeddings):
    return embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

def extract_indices_from_vector(df, user_name,top_k):
    
    # Get user profile
    user_profile = df[df["full_name"] == user_name]
    if user_profile.empty:
        return pd.DataFrame(), "❌ User not found."

    user_gender = user_profile.iloc[0]["gender"]

    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Select the appropriate FAISS index
    if user_gender == "Male":
        matched_df = df[df["gender"] == "Female"]  # Male searches for females
        index_path = r"C:\Users\ThinkPad\Desktop\python projects\matrimony_backend\newvectorstore\female_index.faiss"  # Male users search in the female index
        opposite_gender = "Female"
    elif user_gender== "Female":
        matched_df = df[df["gender"] == "Male"]  # Female searches for males
        index_path = r"C:\Users\ThinkPad\Desktop\python projects\matrimony_backend\newvectorstore\male_index.faiss"  # Female users search in the male index
        opposite_gender = "Male"
    else:
        return pd.DataFrame(), "❌ Invalid gender."

    print(f"🔍 User Gender: {user_gender}, Searching in: {index_path} (Looking for {opposite_gender})")

    # Load the FAISS index
    try:
        index = faiss.read_index(index_path)
    except Exception as e:
        return pd.DataFrame(), f"❌ Error loading FAISS index: {str(e)}"

    # Encode user profile text
    query_text = user_profile.iloc[0]["text"]
    query_embedding = model.encode([query_text]).astype("float32")
    query_embedding = normalize_embeddings(query_embedding)

    # Search FAISS
    distance, faiss_indices = index.search(query_embedding, k=top_k)  # Retrieve extra for filtering
    print(f"FAISS Retrieved Indices: {faiss_indices} and distances: {distance}")
    
    matched_profiles = matched_df.iloc[faiss_indices[0]]  # Ensure only opposite gender profiles are retrieved

    matched_profiles = matched_profiles.head(top_k)  # Return top-k results
    print(f" from search function: {matched_profiles}")
    if matched_profiles.empty:
        return pd.DataFrame(), "❌ No matches found."
    
    return matched_profiles, query_text
