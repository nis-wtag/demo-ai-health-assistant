from api.v1.endpoints import auth, doctors, users
from fastapi import APIRouter

api_router = APIRouter()

api_router = APIRouter(prefix="/v1")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(doctors.router)


@api_router.get("/health", status_code=200)
def health_check():
    return {"status": "ok"}
