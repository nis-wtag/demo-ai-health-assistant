from api.v1.api import api_router
from fastapi import FastAPI

app = FastAPI(title="AI Health Assistant", version="0.1.0")

app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Welcome to the AI Health Assistant (AHA)"}
