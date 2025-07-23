import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def transform_llm_response(llm_response):
    gemini_model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    # Define the user profile schema
    class UserProfile(BaseModel):
        name: str
        preferred_age_range: str
        marital_status: str
        religion: str
        location: str
        education: str
        preferences: str
        
    class ScoreBreakdown(BaseModel):
        mutual_preferences_compatibility : str = Field(description="Extract the Mutual Preferences & Compatibility with precentage and points")
        deeper_alignment_lifestyle : str = Field(description="Extract the Deeper Alignment & Lifestyle with precentage and points")
        reasoning : str = Field(description="Extract the Reasoning text")
        points_to_consider: str = Field(description="Extract the Points to Consider from text")
        compatibility: str = Field(description="Extract the compatibility from the text.")
    
    # Define a model for each match
    class Match(BaseModel):
        object_id: str = Field(description="The object-id (a separate database id that is NOT the same as the profile-id")
        profile_id: int = Field(description="Exctract Profile_id")
        match_score: str = Field(description="Exctract Match Score")
        name: str = Field(description="Extract the Match Name.")
        score_breakdown: ScoreBreakdown

    # Define a model for the overall match analysis
    class MatchAnalysis(BaseModel):
        user_profile: UserProfile
        matches: List[Match]
        conclusion: str
    
    structured_model = gemini_model.with_structured_output(MatchAnalysis)
    
    result = structured_model.invoke(llm_response)
    result_dict = dict(result)
    
    return result_dict