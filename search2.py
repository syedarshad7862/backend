# search_service.py
# from fastapi import FastAPI, Query, HTTPException
from pymongo import MongoClient
import re
import os
from typing import Any, Dict

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
        "delhi":     ["delhi", "new delhi"]
    }
}

STOP_WORDS = {"in", "from", "at", "a", "an", "the", "with", "degree", "all", "and", "of"}

# ------------------------------------------------------------------
# 2.  MongoDB connection (env-variable connection string)
# ------------------------------------------------------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://arshadraza:arshad7862@cluster0.lrpglgh.mongodb.net/")
client = MongoClient(MONGO_URI)
db = client["sumear_matrimony"]
profiles = db["user_profiles"]

# Ensure text index exists (idempotent)
# profiles.create_index([
#     ("native_place", "text"),
#     ("education", "text"),
#     ("height", "text"),
#     ("full_name", "text")
# ])

# ------------------------------------------------------------------
# 3.  Query parser → MongoDB filter
# ------------------------------------------------------------------
# def build_mongo_filter(query: str) -> Dict[str, Any]:
#     """
#     Convert a free-text query such as
#         'female bcom in hyd'
#     into a MongoDB filter dict.
#     """
#     if not query.strip():
#         return {}

#     # normalise string
#     query = query.lower()
#     words = [w for w in re.split(r"[,\s]+", query) if w and w not in STOP_WORDS]

#     # containers for strict and free terms
#     strict: Dict[str, Any] = {}
#     free_terms: list[str] = []

#     # parse known keywords
#     for w in words:
#         matched = False
#         for field, mapping in KEYWORDS.items():
#             # do not overwrite once set
#             if field in strict:
#                 continue
#             for canonical, aliases in mapping.items():
#                 if w in aliases:
#                     strict[field] = re.compile(re.escape(canonical), re.IGNORECASE)
#                     matched = True
#                     break
#             if matched:
#                 break
#         if not matched:
#             free_terms.append(re.escape(w))

#     # Build the final filter
#     mongo_filter: Dict[str, Any] = strict.copy()

#     if free_terms:
#         # one $text query for all unknown terms
#         if "gender" not in strict:
#             mongo_filter["$text"] = {"$search": " ".join(free_terms)}
#         # mongo_filter["$text"] = {"$search": " ".join(free_terms)}
#         # Optional: add a score sort
#         # mongo_filter["$meta"] = "textScore"

#     return mongo_filter

def build_mongo_filter(query: str) -> Dict[str, Any]:
    query = query.lower()
    tokens = [w for w in re.split(r"[,\s]+", query) if w and w not in STOP_WORDS]

    filt: Dict[str, Any] = {}

    # 1.  map recognised tokens to exact/regex filters
    for tok in tokens:
        for field, mapping in KEYWORDS.items():
            for canonical, aliases in mapping.items():
                if tok in aliases:
                    # case-insensitive exact OR substring match
                    # filt[field] = {"$regex": f".*{re.escape(canonical)}.*", "$options": "i"}
                    filt[field] = {"$regex": f"^{re.escape(canonical)}$", "$options": "i"}
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
                {"education": {"$regex": f, "$options": "i"}},
                {"skills":    {"$regex": f, "$options": "i"}},
                {"age": {"$regex": f"^{re.escape(f)}$", "$options": "i"}} if f.isdigit() else {}
            ])
        ors = [o for o in ors if o]
        if ors:
            filt["$or"] = ors

    return filt

# ------------------------------------------------------------------
# 4.  FastAPI route
# ------------------------------------------------------------------
# app = FastAPI(title="Profile Search")

# @app.get("/search")
# def search_profiles(q: str = Query(..., description="Free-text search, e.g. 'female bcom hyd'")):
#     filter_dict = build_mongo_filter(q)
#     if not filter_dict:
#         raise HTTPException(status_code=400, detail="Empty query")

#     cursor = (
#         profiles
#         .find(filter_dict, {"_id": 0})
#         .limit(200)          # basic safety
#     )
#     docs = list(cursor)
#     return {"count": len(docs), "results": docs}


filter_dict = build_mongo_filter('male age 25 in hyderabad mbbs')
cursor = (
        profiles
        .find(filter_dict, {"_id": 0})
        .limit(20)          # basic safety
)
docs = list(cursor)
print(filter_dict)
print(f'"count": {len(docs)}, "results": {docs}')