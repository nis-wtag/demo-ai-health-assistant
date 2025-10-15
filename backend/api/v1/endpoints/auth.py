from core.config import settings
from core.database import get_db
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from schemas.user_schema import UserCreate, UserLogin, UserRead
from services import auth_service
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        user = auth_service.register_user(
            db,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
        )
        return user
    except Exception as e:
        raise HTTPException(400, "Email already registered")


@router.post("/login")
def login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    try:
        tokens = auth_service.login(
            db, email=user_data.email, password=user_data.password
        )

        # Set access token cookie
        response.set_cookie(
            "access_token",
            tokens["access_token"],
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        # Set refresh token cookie
        response.set_cookie(
            "refresh_token",
            tokens["refresh_token"],
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )

        return {"detail": "Logged in successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/logout")
def logout(
    response: Response, access_token: str = Cookie(None), db: Session = Depends(get_db)
):
    try:
        auth_service.logout(db, access_token)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return {"detail": "Logged out successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Invalid access token")


@router.post("/refresh")
def refresh(
    response: Response, refresh_token: str = Cookie(None), db: Session = Depends(get_db)
):
    try:
        tokens = auth_service.refresh(db, refresh_token=refresh_token)

        # Update access token cookie
        response.set_cookie(
            "access_token",
            tokens["access_token"],
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        # Update refresh token cookie
        response.set_cookie(
            "refresh_token",
            tokens["refresh_token"],
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )

        return {"detail": "Tokens refreshed successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Invalid refresh token")
