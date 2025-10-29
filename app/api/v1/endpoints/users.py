from fastapi import APIRouter, Depends, Request
from models.user import User
from schemas.user_schema import UserRead
from services.dependencies.auth_dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserRead,
    status_code=200,
    summary="Retrieves information about the logged in user",
)
def get_my_profile(request: Request, current_user: User = Depends(get_current_user)):
    return current_user
