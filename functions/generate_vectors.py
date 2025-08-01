# import pandas as pd
# from sentence_transformers import SentenceTransformer
# import numpy as np
# import faiss
# import os
# from motor.motor_asyncio import AsyncIOMotorClient

# async def create_faiss_index(mongodb_uri, db_name, collection_name):
#     """Create separate FAISS indexes for male and female profiles."""

#     model = SentenceTransformer("all-MiniLM-L6-v2")
    
#     # Connect to MongoDB
#     client = AsyncIOMotorClient(mongodb_uri)
#     db = client[db_name]
#     collection = db[collection_name]

#     # Fetch data from MongoDB
#     male_data = await collection.find({"gender": "Male"}).to_list(length=None)  # Exclude MongoDB ID
#     female_data = await collection.find({"gender": "Female"}).to_list(length=None)  # Exclude MongoDB ID
#     male_df = pd.DataFrame(male_data)
#     female_df = pd.DataFrame(female_data)
    
#     # Ensure required fields exist
#     required_fields = ["pref_age_range", "pref_marital_status", "pref_complexion", "pref_education", "pref_height", 
#                     "pref_native_place", "pref_maslak_sect", "pref_no_of_siblings", "pref_work_job", "pref_go_to_dargah", "pref_mother_tongue", "pref_deendari","profile_id","sect", "full_name", "date_of_birth", "age", "marital_status", 
#                 "religion","location", "education","mother","father","maslak_sect", "height","religious_practice" ,"native_place",'occupation','preferences',"go_to_dargah"]
#     for field in required_fields:
#         if field not in male_df.columns:
#             male_df[field] = "unknown"
#     for field in required_fields:
#         if field not in female_df.columns:
#             female_df[field] = "unknown"
    
#     # normal keys
#     male_df["text"] = (
#         male_df["profile_id"].astype(str) + " \n" +
#         male_df["full_name"].astype(str) + " \n" +
#         "Date Of Birth: "+ " " + male_df["date_of_birth"].astype(str) + " \n" +
#         "Age: "+ " " + male_df["age"].astype(str) + " \n" +
#         "Marital Status: "+ " " + male_df["marital_status"].astype(str) + " \n" +
#         "Gender: "+ " " + male_df["gender"].astype(str) + " \n" +
#         "complexion: "+ " " + male_df["complexion"].astype(str) + " \n" +
#         "Education: "+ " " + male_df["education"].astype(str) + " \n" +
#         "Height: "+ " " + male_df["height"].astype(str) + " \n" +
#         "Native_place: "+ " " + male_df["native_place"].astype(str) + " \n" +
#         "residence: "+ " " + male_df["residence"].astype(str) + " \n" +
#         "Location: "+ " " + male_df["location"].astype(str) + " \n" +
#         "Father: "+ " " + male_df["father"].astype(str) + " \n" +
#         "Mother: "+ " " + male_df["mother"].astype(str) + " \n" +
#         "sect: "+ " " + male_df["sect"].astype(str) + " \n" +
#         "religious_practice: "+ " " + male_df["religious_practice"].astype(str) + " \n" +
#         "go_to_dargah: "+ " " + male_df["go_to_dargah"].astype(str) + " \n" +
#         "occupation: "+ " " + male_df["occupation"].astype(str) + " \n" +
#         "Preference: "+ " " + male_df["preferences"].astype(str)
#     )
#     female_df["text"] = (
#         female_df["profile_id"].astype(str) + " \n" +
#         female_df["full_name"].astype(str) + " \n" +
#         "Date Of Birth: "+ " " + female_df["date_of_birth"].astype(str) + " \n" +
#         "Age: "+ " " + female_df["age"].astype(str) + " \n" +
#         "Marital Status: "+ " " + female_df["marital_status"].astype(str) + " \n" +
#         "Gender: "+ " " + female_df["gender"].astype(str) + " \n" +
#         "complexion: "+ " " + female_df["complexion"].astype(str) + " \n" +
#         "Education: "+ " " + female_df["education"].astype(str) + " \n" +
#         "Height: "+ " " + female_df["height"].astype(str) + " \n" +
#         "Native_place: "+ " " + female_df["native_place"].astype(str) + " \n" +
#         "residence: "+ " " + female_df["residence"].astype(str) + " \n" +
#         "Location: "+ " " + female_df["location"].astype(str) + " \n" +
#         "Father: "+ " " + female_df["father"].astype(str) + " \n" +
#         "Mother: "+ " " + female_df["mother"].astype(str) + " \n" +
#         "sect: "+ " " + female_df["sect"].astype(str) + " \n" +
#         "religious_practice,: "+ " " + female_df["religious_practice"].astype(str) + " \n" +
#         "go_to_dargah: "+ " " + female_df["go_to_dargah"].astype(str) + " \n" +
#         "occupation: "+ " " + female_df["occupation"].astype(str) + " \n" +
#         "Preference: "+ " " + female_df["preferences"].astype(str)
#     )
#     # texts = female_df["text"].tolist()
    
#     male_embeddings = model.encode(male_df["text"].tolist()).astype("float32")
#     female_embeddings = model.encode(female_df["text"].tolist()).astype("float32")
    
#     #     # Normalize embeddings
#     male_embeddings /= np.linalg.norm(male_embeddings, axis=1, keepdims=True)
#     female_embeddings /= np.linalg.norm(female_embeddings, axis=1, keepdims=True)

#     # Create FAISS indexes **SEPARATELY**
#     male_index = faiss.IndexFlatL2(male_embeddings.shape[1])
#     female_index = faiss.IndexFlatL2(female_embeddings.shape[1])

#     male_index.add(male_embeddings)  # type: ignore # Male Index (to match Females)
#     female_index.add(female_embeddings)  # type: ignore # Female Index (to match Males)

#     os.makedirs("newvectorstore", exist_ok=True)

#     # Save FAISS indexes separately
#     faiss.write_index(male_index, "newvectorstore/male_index.faiss")   # Male users will search here (matches Female)
#     faiss.write_index(female_index, "newvectorstore/female_index.faiss")  # Female users will search here (matches Male)

#     print("✅ FAISS indexes created successfully.")
    


import pandas as pd
from sentence_transformers import SentenceTransformer
from motor.motor_asyncio import AsyncIOMotorClient
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from tqdm import tqdm

async def create_qdrant_indexes(mongodb_uri, db_name, collection_name):
    """Create separate Qdrant collections for male and female profiles."""

    # Connect to MongoDB
    client = AsyncIOMotorClient(mongodb_uri)
    db = client[db_name]
    collection = db[collection_name]

    # Fetch profiles
    male_data = await collection.find({"gender": "Male"}).to_list(length=None)
    female_data = await collection.find({"gender": "Female"}).to_list(length=None)

    male_df = pd.DataFrame(male_data)
    female_df = pd.DataFrame(female_data)

    # Embedding model
    sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Qdrant setup
    qdrant_url = "https://6cc74303-ab87-438b-bc32-f225f7e038d1.europe-west3-0.gcp.cloud.qdrant.io:6333"
    qdrant_api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.o30xdRs_ctcJmTCw2DVWab7UQ6gWKbJPTvEwHXFsLX4"
    qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key, timeout=60.0)

    # --- Helper function to preprocess text ---
    def prepare_text(df):
        df.fillna("unknown", inplace=True)
        df["text"] = (
            
            "object-id: "+ " " + df["_id"].astype(str) + " \n" +
            "profile_id: "+ " " + df["profile_id"].astype(str) + " \n" +
            "Full Name: "+ " " + df["full_name"].astype(str) + " \n" +
            "Date Of Birth: "+ " " + df["date_of_birth"].astype(str) + " \n" +
            "Age: "+ " " + df["age"].astype(str) + " \n" +
            "Marital Status: "+ " " + df["marital_status"].astype(str) + " \n" +
            "Gender: "+ " " + df["gender"].astype(str) + " \n" +
            "complexion: "+ " " + df["complexion"].astype(str) + " \n" +
            "Education: "+ " " + df["education"].astype(str) + " \n" +
            "Height: "+ " " + df["height"].astype(str) + " \n" +
            "Native_place: "+ " " + df["native_place"].astype(str) + " \n" +
            "residence: "+ " " + df["residence"].astype(str) + " \n" +
            "Location: "+ " " + df["location"].astype(str) + " \n" +
            "Father: "+ " " + df["father"].astype(str) + " \n" +
            "Mother: "+ " " + df["mother"].astype(str) + " \n" +
            "sect: "+ " " + df["sect"].astype(str) + " \n" +
            "religious_practice,: "+ " " + df["religious_practice"].astype(str) + " \n" +
            "go_to_dargah: "+ " " + df["go_to_dargah"].astype(str) + " \n" +
            "occupation: "+ " " + df["occupation"].astype(str) + " \n" +
            "Preference: "+ " " + df["preferences"].astype(str)
        )
        return df

    # --- Function to add documents to Qdrant ---
    def add_to_qdrant(df, collection_name,batch_size=100):
        # Recreate Qdrant collection
        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        # Create LangChain Qdrant wrapper
        vectorstore = Qdrant(
            client=qdrant_client,
            collection_name=collection_name,
            embeddings=embedding_model,
        )
        # Create documents
        # docs = [Document(page_content=txt) for txt in texts]
        docs = [
            Document(
                page_content=row["text"],
                metadata={
                    "profile_id": str(row["_id"]),
                    "full_name": row["full_name"],
                    "gender": row["gender"]
                }
            )
            for _, row in df.iterrows()
        ]

        
        print(f"Uploading {len(docs)} documents to Qdrant collection: {collection_name}")
        for i in tqdm(range(0, len(docs), batch_size), desc=f"Uploading to {collection_name}"):
            batch = docs[i:i + batch_size]
            vectorstore.add_documents(batch)
            
        print(f"✅ Uploaded {len(docs)} documents to Qdrant collection: {collection_name}")

    # Prepare and upload
    add_to_qdrant(prepare_text(male_df), "male_profiles")
    add_to_qdrant(prepare_text(female_df), "female_profiles")
