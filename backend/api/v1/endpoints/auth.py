from datetime import datetime, timedelta, timezone

from config.settings import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    COOKIE_HTTPONLY,
    COOKIE_SAMESITE,
    COOKIE_SECURE,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from backend.services.auth_service import create_session, invalidate_session
from backend.services.auth_service import authenticate_user, create_user
from db.postgres import get_db
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from models.session import Session as SessionModel
from backend.schemas.user_schema import UserCreate, UserLogin
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["Auth"])


def generate_access_token(user_id):
    return f"access-{user_id}-{datetime.now(timezone.utc).timestamp()}"


def generate_refresh_token(user_id):
    return f"refresh-{user_id}-{datetime.now(timezone.utc).timestamp()}"


@router.post("/register")
def register(form_data: UserCreate, db: Session = Depends(get_db)):
    user = create_user(db, form_data)
    if user:
        return {"detail": "User registered successfully"}
    else:
        raise HTTPException(400, "Email already registered")


@router.post("/login")
def login(form_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = generate_access_token(user.id)
    refresh_token = generate_refresh_token(user.id)
    access_expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    refresh_expires_at = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    create_session(
        db,
        user_id=user.id,
        access_token=access_token,
        refresh_token=refresh_token,
        access_expires_at=access_expires_at,
        refresh_expires_at=refresh_expires_at,
    )

    # set cookies
    response.set_cookie(
        "access_token",
        access_token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return {"detail": "Logged in successfully"}


@router.post("/logout")
def logout(
    response: Response, access_token: str = Cookie(None), db: Session = Depends(get_db)
):
    session = (
        db.query(SessionModel).filter(SessionModel.access_token == access_token).first()
    )
    if session:
        invalidate_session(db, session)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
    return {"detail": "Logged out successfully"}


@router.post("/refresh")
def refresh_access_token(
    response: Response, refresh_token: str = Cookie(...), db: Session = Depends(get_db)
):
    old_session = (
        db.query(SessionModel)
        .filter(SessionModel.refresh_token == refresh_token, SessionModel.is_valid)
        .first()
    )
    if not old_session or old_session.refresh_expires_at < datetime.now(timezone.utc):
        raise HTTPException(401, "Invalid or expired refresh token")

    invalidate_session(db, old_session)

    new_access_token = generate_access_token(old_session.user_id)

    create_session(
        db,
        user_id=old_session.user_id,
        access_token=new_access_token,
        refresh_token=old_session.refresh_token,
        access_expires_at=datetime.now(timezone.utc)
        + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        refresh_expires_at=datetime.now(timezone.utc)
        + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    response.set_cookie(
        "access_token",
        new_access_token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        "refresh_token",
        old_session.refresh_token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return {"detail": "Tokens refreshed successfully"}
