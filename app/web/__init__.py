from fastapi import APIRouter
from web.routes import auth, dashboard, chat

router = APIRouter()

# Include all web page routers
router.include_router(auth.router)
router.include_router(dashboard.router)
router.include_router(chat.router)
