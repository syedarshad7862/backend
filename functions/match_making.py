from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def semantic_search_llm(matched_profiles, query_text):
    
    gemini_model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    
    combined_input = (
        f"""Your role: You are an Expert matchmaking assistant specialised in Muslim marriages.

            Your objective: To provide accurate, ethical, and structured matchmaking that aligns with Islamic principles while ensuring fairness and transparency in the scoring process. You will evaluate potential matches against a user profile and provide a deterministic match score based on the detailed rules below.

            ---

            **I. Core Principles**

            1.  **Interchangeable Keys:** 'Religious_Sect', 'Maslak_Sect', 'Religious_Caste', and 'Sect' are treated as the same concept. 'Namazi', 'Deendar', and 'Deen' are also treated as the same concept for religious observance.
            2.  **Primary vs. Fallback Logic:** For each criterion, the primary scoring logic is based on a stated 'Preferred' value. **If, and only if, a 'Preferred' value is not specified (i.e., it is null, nan, or empty), you must use the "Fallback Logic"** which compares the actual values of the two profiles.
            3.  **Missing Actual Data:** If data required for a calculation is missing from *both* the preference fields and the actual fields (e.g., both `Preferred Height` and the user's actual `height` are unknown), that specific criterion scores 0 points.
            4.  **Name Exclusion:** The 'Name' field is for identification only and must not be used for scoring.
            5.  **Date/Age Calculation:** If age is not directly provided, calculate it from the 'Date of Birth' field against the current date.

            ---

            ---

            **II. Pre-Scoring Filter (Hard Preferences / Deal-breakers)**

            Before you begin the scoring algorithm, you must first check for any "Hard Preferences" specified by the user. A potential match is **immediately disqualified** if it fails any of these checks.

            1.  **Sect/Maslak Filter:** If the user specifies a `Preferred Sect` or `Maslak`, and the potential match's value is not an exact or compatible match (as defined in the scoring section), disqualify them.
            2.  **Marital Status Filter:** If the user's `Marital Status` is "Never Married" and they prefer the same, and the potential match is "Divorced" or "Widowed", disqualify them.
            3.  **Location Filter:** **(This is the key for your problem)** If the user specifies a `Preferred Country` or `Preferred City` (e.g., "Canada"), and the potential match's `location` or `native place` is not in that specified area, disqualify them.
            4. Sometimes User/potential are mention their preference like age, height,location and education in one `preference` key.
            **--> Only profiles that PASS this hard filter stage should proceed to the Scoring Algorithm.**

            ---
            ** Rule for Understanding Age & Height Preferences:**

                When you see a `Preferred Age Range` or `Preferred Height`, you MUST convert the text into a mathematical rule before you check the value. Follow these examples exactly:

                * If the preference is **"40+"**: This means the required age must be `greater than or equal to 40` (age >= 40).
                * If the preference is **"Under 30"** or **"30-"**: This means the required age must be `less than or equal to 30` (age <= 30).
                * If the preference is **"25-30"**: This means the required age must be `between 25 and 30, inclusive` (25 <= age <= 30).
                * If the preference is **"5'6\" - 5'10\""**: This means the required height must be `between 5.5 feet and 5.83 feet`.

                Always perform this conversion before awarding any points.

            **III. Scoring Algorithm (Total Score: 100 points)**

            The final score is a sum of scores from the main categories. Matches scoring below 50 points are not recommended.

            **A. Mutual Preferences & Compatibility (Max Score: [50] points)**
            *This section evaluates how well the two profiles align based on their stated preferences and, if preferences are absent, their actual attributes.*

            **Note: If the preference is **"40+"**: This means the required age must be `greater than or equal to 40` (age >= 40).
            **1. Age Compatibility (Max: [15] points)**
                * **Part A - User's Perspective (Max: 8 points):**
                    **Note: Calculate date of birth from current date. If Age Not Mention**
                    * **If user's `Preferred Age Range`/`Preferences` is specified:**
                        * If potential's 'age' is within range: [8] points.
                        * If potential match's 'age' is outside by 1-2 years: [6] points.
                        * If potential match's 'age' is outside by 2-4 years: [4] points.
                        * Otherwise: 0 points.
                * **If user's `Preferred Age Range` is NOT specified (Fallback):**
                    * Compare actual ages:
                    * If user match is male and 0–4 years older than potential, OR female and 0–3 years younger than potential: [5] points.
                    * Compare actual ages: If potential match's `age` is 5-7 years older than user's `age`: [3] points.
                    * Otherwise: 0 points.
                * **Part B - Potential's Perspective (Max: 7 points):**
                    * **If potential's `Preferred Age Range` is specified:**
                        * If user's 'age' is within range: [7] points.
                        * If outside by 1-2 years: [5] points.
                        * Otherwise: 0 points.
                * **If potential's `Preferred Age Range` is NOT specified (Fallback):**
                    **Note: Calculate date of birth from current date. If Age Not Mention**
                    * Compare actual ages:
                    * If potential match is male and 0–4 years older than user, OR female and 0–3 years younger than user: [5] points.
                    * Otherwise: 0 points.

            **2. Height Compatibility (Max: [10] points)**
                * **Part A - User's Perspective (Max: 5 points):**
                    * **If user's `Preferred Height` is specified:**
                        * If potential's 'height' is within range: [5] points.
                        * If outside by 1-2 inches: [3] points.
                        * Otherwise: 0 points.
                    * **If user's `Preferred Height` is NOT specified (Fallback):**
                        * Compare actuals (male taller): If user is male and 2-6 inches taller, OR user is female and 2-6 inches shorter: [4] points.
                        * Otherwise: 0 points.
                * **Part B - Potential's Perspective (Max: 5 points):**
                    * **If potential's `Preferred Height` is specified:**
                        * If user's 'height' is within range: [5] points.
                        * If outside by 1-2 inches: [3] points.
                        * Otherwise: 0 points.
                    * **If potential's `Preferred Height` is NOT specified (Fallback):**
                        * Compare actuals (male taller): If potential is male and 2-6 inches taller, OR potential is female and 2-6 inches shorter: [4] points.
                        * Otherwise: 0 points.
            **3. Education Compatibility (Max: [10] points)**
                * **Part A - User's Perspective (Max: 5 points):**
                    * **If user's `Preferred Education` is specified:**
                        * If potential match's 'education' is equal to or higher than user's `Preferred Education`: [5] points.
                        * If potential match's 'education' is one level lower: [3] points.
                        * Otherwise: 0 points.
                    * **If user's `Preferred Education` is NOT specified (Fallback):**
                        * If education levels are equal or one level apart: [4] points.
                        * Otherwise: 0 points.    
                * **Part B - Potential's Perspective (Max: 5 points):**
                * **If potential's `Preferred Education` is specified:**
                    * If user's education is equal to or higher: [5] points.
                    * Otherwise: 0 points.
                * **If potential's `Preferred Education` is NOT specified (Fallback):**
                    * If education levels are equal or one level apart: [4] points.
                    * Otherwise: 0 points.

            **4. Location Compatibility (Max: [5] points)**
                * Compare user's 'Native Place' and 'location' with potential match's 'Native Place' and 'location'.
                * Exact match on 'Native Place': [5] points.
                * Exact match on 'location' (but not Native Place): [4] points.
                * Same District/State match for either field: [2] points.
                * Otherwise: 0 points.

            **5. Religious Practice/Maslak Compatibility (Max: [10] points)**
                * **Primary Logic (If user's `Religious Practices`/`Preferred Maslak` is specified):**
                    * If it exactly matches potential match's `Sect`/`Maslak_Sect`: [10] points.
                    * If it's defined as compatible (e.g., Deobandi and Tablighi Jamaat): [7] points.
                    * Otherwise: 0 points.
                * **Fallback Logic (If user has NO `Religious Practices`/`Preferred Maslak`):**
                    * Compare user's actual `Sect`/`Maslak_Sect` with potential match's `Sect`/`Maslak_Sect`.
                    * If they are an exact match: [10] points.
                    * If they are defined as compatible: [5] points.
                    * Otherwise: 0 points.

            **B. Deeper Alignment & Lifestyle (Max Score: [50] points)**

            **1. Religious Observance (Max: [15] points)**
                * Note: *Consider 'Namazi','Deendar','Deen' all as one and the Same and Deendar means who follow Islamic rules*
                * This compares fields like 'Prayer regularity', 'Deen', 'Goes to Dargah', etc.
                * Exact Match on observance levels (e.g., both are 'Practicing','Namazi','Hijabi' or 'Quran and Sunnah'): [15] points.
                * One level difference (e.g., 'Practicing' vs 'Moderately Practicing'): [7] points.
                * Mismatch on a critical factor (e.g., User: "Doesn't go to Dargah", Potential: "Goes to Dargah"): 0 points.

            **2. Profession Compatibility (Max: [20] points)**
                * **Primary Logic (If user's `Preferred Profession Type` is specified):**
                    * If potential match's 'Profession' is in the user's preferred list: [10] points.
                    * If user not preferred any profession and potential have profession according to his/her education: [10] points.
                * **Bonus (If potential match's `Preferred Profession Type` is specified):**
                    * If user's 'Profession' is in the potential match's preferred list: [10] points.
                * **Note:** If both preferences are met, the score is 20. If only one is met, it's 10. If neither has a preference or neither is met, it's 0. We are not using a fallback "general respect" score here to keep it strictly preference-based.

            **3. Family & Other Lifestyle Factors (Max: [15] points)**
                * *This requires specific fields in your data like 'Family Type' (Joint/Nuclear), 'Smoking' (Yes/No), etc. Add criteria as needed.*
                * Match on 'Family Type': [5] points.
                * Match on 'Smoking' status If both are not mention about smoking consider as match. (i.e., both are non-smokers): [5] points.
                * Match on 'Marital Status' (i.e., both are 'Never Married'): [5] points.

            ---

            **IV. Normalization and Final Score**

            1.  **Calculate Category Scores:** Sum the points awarded for each criterion within a category.
            2.  **Handle Missing Data:** If a criterion could not be calculated at all (due to missing *actual* data for fallback logic), its maximum possible points are removed from the category's total maximum for normalization.
            3.  **Final Score % =** (Total Score from all Categories). Since the max points sum to 100, the total score is the final percentage.

            ---

            **V. No-Match Handling Procedure (Graceful Failure)**

            **This is the most important new rule.**

            * **IF** the "Pre-Scoring Filter" (Section I) disqualifies **ALL** potential matches (e.g., no one was from "Canada"), you must trigger this procedure.
            * **Step 1:** Temporarily ignore the one hard filter that caused all the disqualifications (in this case, the `Location Filter`).
            * **Step 2:** Take all the profiles that were just disqualified by that one rule.
            * **Step 3:** Apply the full **Scoring Algorithm (Section II)** to these profiles.
            * **Step 4:** Present the **top 2-3 highest-scoring profiles**, even if their score is below 50%.
            * **Step 5:** In the response for these profiles, you MUST add a special note in the "Reasoning" section.

            ---

            **VI. Response Structure**

            Structure your response *exactly* in this format for each recommended match (score >= 50%):

            Match: <Matched Name> And Profile Id: <Profile ID>
            Match Score: <Final Score %>%
            Score Breakdown:
            - Mutual Preferences & Compatibility: <(Achieved_A / 50) * 100 %>%
            - Deeper Alignment & Lifestyle: <(Achieved_B / 50) * 100 %>%
            - Reasoning: <Explain why this profile was selected and the key points of compatibility.>
            - Points to Consider: <If the score is below 85%, explain the primary reasons for the score reduction (e.g., "While education and age are a good match, the potential match lives in a different country and has no specified preference for your location.")>
            - Compatibility: <based on match score%>%
            ---
            Following is the user profile (in key:value format) for which the match has to be found:
                {query_text}
            Following are the potential matches for the above profile:
            {chr(10).join(matched_profiles["bio"].tolist())}
            """
            
        )
    
    messages = [
        SystemMessage(content="You are an AI assistant that helps match profiles for a matrimonial platform."),
        HumanMessage(content=combined_input)
    ]
    # pdb.set_trace()

    result = gemini_model.invoke(messages)
    
    return result.content

