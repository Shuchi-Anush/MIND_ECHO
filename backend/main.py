from fastapi import FastAPI
from backend.routers import example, voice, sentiment
from backend.services import sentiment_engine
from mental_health_ai.companion import start_mental_health_session

app = FastAPI(
    title="MIND_ECHO API",
    description="Backend API for the Personalized Mental Health Companion Project.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to MIND_ECHO API"}

# Include the routers (you can add prefix in individual routers)
app.include_router(example.router)
app.include_router(voice.router)
app.include_router(sentiment.router)

def main():
    print("Welcome to MIND_ECHO 🌟")
    print("1. Start Mental Health Companion")
    print("2. Exit")

    choice = input("Choose an option: ")
    if choice == '1':
        start_mental_health_session()
    else:
        print("Goodbye!")

if __name__ == "__main__":
    main()