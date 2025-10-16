from api.v1.api import api_router as api_v1_router
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from web.routes import router as web_router

app = FastAPI(title="AI Health Assistant", version="0.1.0")

app.include_router(api_v1_router)

app.mount("/static", StaticFiles(directory="web/static"), name="static")

app.include_router(web_router, tags=["Web"])


@app.get("/")
def root():
    return {"message": "Welcome to the AI Health Assistant (AHA)"}
