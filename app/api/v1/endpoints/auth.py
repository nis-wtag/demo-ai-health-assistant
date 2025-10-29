from core.config import settings
from core.database import DbSession
from core.limiter import limiter
from fastapi import APIRouter, Cookie, Request, Response
from schemas.user_schema import UserCreate, UserLogin, UserRead
from services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register", response_model=UserRead, status_code=201, summary="Register a new user"
)
@limiter.limit("5/minute")
def register(request: Request, user_data: UserCreate, db: DbSession):
    return auth_service.register_user(
        db,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
    )


@router.post(
    "/login",
    response_model=UserRead,
    status_code=200,
    summary="Authenticate user and issue tokens",
)
@limiter.limit("5/minute")
def login(request: Request, user_data: UserLogin, response: Response, db: DbSession):
    user, access_token, refresh_token = auth_service.login(
        db, email=user_data.email, password=user_data.password
    )

    # Set access token cookie
    response.set_cookie(
        "access_token",
        access_token,
        httponly=settings.COOKIE_HTTPONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    # Set refresh token cookie
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=settings.COOKIE_HTTPONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return user


@router.post(
    "/logout", status_code=200, summary="Logout user and clear authentication cookies"
)
def logout(
    request: Request,
    response: Response,
    db: DbSession,
    access_token: str = Cookie(None),
):
    auth_service.logout(db, access_token)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"detail": "Logged out successfully"}
