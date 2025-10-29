from api.v1.endpoints import auth, chambers, chat, dashboard, doctors, users
from fastapi import APIRouter

api_router = APIRouter()

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(doctors.router)
api_router.include_router(chambers.router)
api_router.include_router(chat.router)
api_router.include_router(dashboard.router)


@api_router.get("/health", status_code=200)
def check_health():
    return {"status": "ok"}
