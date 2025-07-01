from fastapi import FastAPI
from routes import auth, dashboard
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

origins = [
    "http://localhost:4200",  # Default Angular dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(auth.router)
app.include_router(dashboard.router)

@app.get('/')
def home():
    return {"message": "hello world"}