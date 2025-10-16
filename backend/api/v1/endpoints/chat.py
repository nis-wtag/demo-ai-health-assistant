from core.database import get_db
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request
from models.user import User, UserRole
from schemas.user_schema import UserRead
from services.dependencies.auth_dependencies import get_current_user, require_roles

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/")
def get_my_profile(request: Request, current_user: User = Depends(get_current_user)):
    return {"reply": "Hello Nayem"}
