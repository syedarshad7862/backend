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
        "delhi":     ["delhi", "new delhi"],
        "canada": ["canada","Canada"]
    },
    
    "education": {
    # MBBS / medical
    "mbbs":      ["mbbs", "m.b.b.s", "m b b s", "bachelor of medicine", "bachelor of medicine & surgery", "mbchb", "md", "doctor of medicine"],

    # engineering
    "b.e":       ["b.e", "be", "bachelor of engineering", "b.tech", "btech", "bachelor of technology", "m.e", "me", "m.tech", "mtech"],
    "b.tech":       ["bachelor of engineering", "b.tech", "btech", "bachelor of technology", "B.tech", "btech","B-tech"],

    # commerce
    "b.com":     ["b.com", "bcom", "bachelor of commerce", "m.com", "mcom", "master of commerce"],

    # science
    "b.sc":      ["b.sc", "bsc", "bachelor of science", "m.sc", "msc", "master of science"],

    # business administration
    "bba":       ["bba", "bachelor of business administration", "mba", "master of business administration"],

    # arts / humanities
    "ba":        ["ba", "b.a", "bachelor of arts", "m.a", "ma", "master of arts"],

    # pharmacy
    "b.pharm":   ["b.pharm", "bpharm", "bachelor of pharmacy"],

    # computer applications
    "bca":       ["bca", "bachelor of computer applications", "mca", "master of computer applications"],

    # diploma / polytechnic
    "diploma":   ["diploma", "polytechnic", "poly"]
},
"marital_status":{
        "single": ["Single", "single"],
        "Unmarried": ["Unmarried", "Unmarried"]
    },
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
#     query = query.lower()
#     tokens = [w for w in re.split(r"[,\s]+", query) if w and w not in STOP_WORDS]

#     filt: Dict[str, Any] = {}

#     # 1.  recognise keywords
#     for tok in tokens:
#         for field, mapping in KEYWORDS.items():
#             for canonical, aliases in mapping.items():
#                 if tok in aliases:
#                     # substring, case-insensitive
#                     pat = "|".join(map(re.escape, aliases))
#                     filt[field] = {"$regex": pat, "$options": "i"}
#                     break

#     # 2.  remaining tokens (age, unknown)
#     known = {alias for m in KEYWORDS.values()
#              for lst in m.values() for alias in lst}
#     extra = [t for t in tokens if t not in known]

#     ors = []
#     for tok in extra:
#         if tok.isdigit():
#             filt["age"] = {"$regex": tok, "$options": "i"}
#         else:
#             ors.extend([
#                 {"education": {"$regex": tok, "$options": "i"}},
#                 {"skills":    {"$regex": tok, "$options": "i"}}
#             ])
#     ors = [o for o in ors if o]
#     if ors:
#         filt["$or"] = ors

#     return filt

def build_mongo_filter(query: str) -> Dict[str, Any]:
    query = query.lower()
    tokens = [w for w in re.split(r"[,\s]+", query) if w and w not in STOP_WORDS]

    filt: Dict[str, Any] = {}

    # 1.  map recognised tokens to exact/regex filters
    for tok in tokens:
        for field, mapping in KEYWORDS.items():
            for canonical, aliases in mapping.items():
                if tok in aliases:
                    if field in ("gender", "native_place"):
                        filt[field] = {"$regex": f"^{re.escape(canonical)}$", "$options": "i"}
                    else:
                        alias_pattern = "|".join(map(re.escape, aliases))
                        filt[field] = {"$regex": alias_pattern, "$options": "i"}
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
                {"education": {"$regex": f"\\b{re.escape(f)}\\b", "$options": "i"}},
                {"residence":    {"$regex": f"\\b{re.escape(f)}\\b", "$options": "i"}},
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


filter_dict = build_mongo_filter('male canada')
page = 1
limit = 6                       # no comma
skip_ = (page - 1) * limit

cursor = (
    profiles
    .find(filter_dict)          # include _id by default
    .skip(skip_)
    .limit(limit)
)

docs = list(cursor)
print(filter_dict)
print(f'"count": {len(docs)}, "results": {docs}')