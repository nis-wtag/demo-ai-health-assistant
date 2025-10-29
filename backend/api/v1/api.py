from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/health", status_code=200)
def health_check():
    return {"status": "ok"}
