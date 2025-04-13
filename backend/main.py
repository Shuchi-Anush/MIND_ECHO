# backend/main.py
from fastapi import FastAPI
from backend.routers import example, voice  # Import both routers

app = FastAPI(
    title="MIND_ECHO API",
    description="Backend API for the Personalized Mental Health Companion Project.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to MIND_ECHO API"}

# Include the routers (no additional prefix needed here if paths are defined in the router)
app.include_router(example.router)
app.include_router(voice.router)
