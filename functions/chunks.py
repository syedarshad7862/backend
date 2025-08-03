import pandas as pd
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()
async def create_chunks(mongodb_uri, db_name, collection_name):
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongodb_uri)
    db = client[db_name]
    collection = db[collection_name]

    # Fetch data from MongoDB
    data = await collection.find({}).to_list(length=None)  # Exclude MongoDB ID
    df = pd.DataFrame(data)

    # Ensure required fields exist
    required_fields = ["pref_age_range", "pref_marital_status", "pref_complexion", "pref_education", "pref_height", 
                    "pref_native_place", "pref_maslak_sect", "pref_no_of_siblings", "pref_work_job", "pref_go_to_dargah", "pref_mother_tongue", "pref_deendari","profile_id","sect", "religious_practice", "full_name", "date_of_birth", "age","gender", "marital_status","maslak_sect","religion", 
                "religion", "education", "father" ,"mother", "father_name", "height", "native_place","ethnicity",'occupation','preferences',"pref_location","pref_own_house","religious_sect"]
    for field in required_fields:
        if field not in df.columns:
            df[field] = "unknown"
    # pk
    df["text"] = (
        "object-id: "+ " " + df["_id"].astype(str) + " \n" +
        "Name"+" " + df["full_name"].astype(str) + " \n" +
        "Date Of Birth: "+ " " + df["date_of_birth"].astype(str) + " \n" +
        "Age: "+ " " + df["age"].astype(str) + " \n" +
        "Gender: "+ " " + df["gender"].astype(str) + " \n" +
        "Height: "+ " " + df["height"].astype(str) + " \n" +
        "Marital Status: "+ " " + df["marital_status"].astype(str) + " \n" +
        "Education: "+ " " + df["education"].astype(str) + " \n" +
        "Sect: "+ " " + df["sect"].astype(str) + " \n" +
        "Maslak sect: "+ " " + df["maslak_sect"].astype(str) + " \n" +
        "Religion: "+ " " + df["religion"].astype(str) + " \n" +
        "Native place: "+ " " + df["native_place"].astype(str) + " \n" +
        "Residence/Location: "+ " " + df["residence"].astype(str) + " \n" +
        "Preferred Age Range: "+ " " + df["pref_age_range"].astype(str) + " \n" +
        "Preferred Marital Status: "+ " " + df["pref_marital_status"].astype(str) + " \n" +
        "Preferred Complexion: "+ " " + df["pref_complexion"].astype(str) + " \n" +
        "Preferred Education: "+ " " + df["pref_education"].astype(str) + " \n" +
        "Preferred Height: "+ " " + df["pref_height"].astype(str) + " \n" +
        "Preferred Native_place: "+ " " + df["pref_native_place"].astype(str) + " \n" +
        "Preferred Maslak_sect: "+ " " + df["pref_maslak_sect"].astype(str) + " \n" +
        "Preferred Occupation: "+ " " + df["pref_work_job"].astype(str) + " \n" +
        "Go to dargah: "+ " " + df["pref_go_to_dargah"].astype(str) + " \n" +
        "Preference Mother tongue: "+ " " + df["pref_mother_tongue"].astype(str) + " \n" +
        "Deendar: "+ " " + df["pref_deendari"].astype(str) + " \n" +
        "Preferred location: "+ " " + df["pref_location"].astype(str) + " \n" +
        "Religious practice: "+ " " + df["religious_practice"].astype(str) + " \n" +
        "Preferred own house: "+ " " + df["pref_own_house"].astype(str) + " \n" +
        "Preferences: "+ " " + df["preferences"].astype(str)
    )
    
    df["bio"] = (
        "object-id: "+ " " + df["_id"].astype(str) + " \n" +
        "profile_id: "+ " " + df["profile_id"].astype(str) + " \n" +
        "Full Name: "+ " " + df["full_name"].astype(str) + " \n" +
        "Date Of Birth: "+ " " + df["date_of_birth"].astype(str) + " \n" +
        "Age: "+ " " + df["age"].astype(str) + " \n" +
        "Gender: "+ " " + df["gender"].astype(str) + " \n" +
        "Marital Status: "+ " " + df["marital_status"].astype(str) + " \n" +
        "Gender: "+ " " + df["gender"].astype(str) + " \n" +
        "complexion: "+ " " + df["complexion"].astype(str) + " \n" +
        "Education: "+ " " + df["education"].astype(str) + " \n" +
        "Height: "+ " " + df["height"].astype(str) + " \n" +
        "Native_place: "+ " " + df["native_place"].astype(str) + " \n" +
        "legal status: "+ " " + df["legal_status"].astype(str) + " \n" +
        "ethnicity: "+ " " + df["ethnicity"].astype(str) + " \n" +
        "residence: "+ " " + df["residence"].astype(str) + " \n" +
        "Father: "+ " " + df["father"].astype(str) + " \n" +
        "Mother: "+ " " + df["mother"].astype(str) + " \n" +
        "Sect: "+ " " + df["sect"].astype(str) + " \n" +
        "Maslak sect: "+ " " + df["maslak_sect"].astype(str) + " \n" +
        "religious_practice: "+ " " + df["religious_practice"].astype(str) + " \n" +
        "occupation: "+ " " + df["occupation"].astype(str) + " \n" +
        "Preference: "+ " " + df["preferences"].astype(str) + " \n" +
        "Preferred Age Range: "+ " " + df["pref_age_range"].astype(str) + " \n" +
        "Preferred Marital Status: "+ " " + df["pref_marital_status"].astype(str) + " \n" +
        "Preferred Maslak_sect: "+ " " + df["pref_maslak_sect"].astype(str) + " \n" +
        "Preferred location: "+ " " + df["pref_location"].astype(str)
    )
    # print(df["bio"])
    # Convert the combined text to a list
    texts = df["text"].tolist()
    return texts,df