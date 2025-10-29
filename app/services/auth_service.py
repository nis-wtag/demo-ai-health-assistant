import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from core.config import settings
from core.exceptions import EmailAlreadyRegisteredException, InvalidCredentialsException
from models.user import User
from passlib.context import CryptContext
from repositories.user_repository import user_repository
from sqlalchemy.orm import Session

from services import session_service

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# -------------------------------
# Password Utilities
# -------------------------------
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# -------------------------------
# Token Utilities
# -------------------------------
def generate_token(user: User, iat: datetime, exp: datetime):
    raw_string = f"{uuid.uuid4()}-{user.id}-{datetime.now(timezone.utc).timestamp()}"
    return hashlib.sha256(raw_string.encode()).hexdigest()


# -------------------------------
# Services
# -------------------------------
def register_user(db: Session, email: str, password: str, full_name: str):
    existing_user = user_repository.get_by_email(db, email=email)
    if existing_user:
        raise EmailAlreadyRegisteredException()

    hashed_password = get_password_hash(password)
    return user_repository.create(
        db, email=email, hashed_password=hashed_password, full_name=full_name
    )


def authenticate_user(db: Session, email: str, password: str):
    user = user_repository.get_by_email(db, email=email)
    if not user or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsException()
    return user


def login(db: Session, email: str, password: str):
    user = authenticate_user(db, email=email, password=password)

    access_token_iat = refresh_token_iat = datetime.now(timezone.utc)
    access_token_exp = access_token_iat + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    refresh_token_exp = refresh_token_iat + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )

    access_token = generate_token(user, iat=access_token_iat, exp=access_token_exp)
    refresh_token = generate_token(user, iat=refresh_token_iat, exp=refresh_token_exp)

    session_service.create_session(
        db,
        user_id=user.id,
        access_token=access_token,
        refresh_token=refresh_token,
        access_expires_at=access_token_exp,
        refresh_expires_at=refresh_token_exp,
    )

    return user, access_token, refresh_token


def logout(db: Session, access_token: str):
    session = session_service.get_by_access_token(db, access_token)
    if session:
        session_service.invalidate_session(db, session)
    else:
        raise InvalidCredentialsException(detail="Invalid access token")


def refresh(db: Session, refresh_token: str):
    old_session = session_service.get_by_refresh_token(db, refresh_token)

    if not old_session or old_session.refresh_expires_at < datetime.now(timezone.utc):
        raise InvalidCredentialsException("Invalid or expired refresh token")

    session_service.invalidate_session(db, old_session)

    user = user_repository.get_by_id(db, old_session.user_id)
    new_access_token_iat = new_refresh_token_iat = datetime.now(timezone.utc)
    new_access_token_exp = new_access_token_iat + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    new_refresh_token_exp = new_refresh_token_iat + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )

    new_access_token = generate_token(
        user, iat=new_access_token_iat, exp=new_access_token_exp
    )
    new_refresh_token = generate_token(
        user, iat=new_refresh_token_iat, exp=new_refresh_token_exp
    )

    session_service.create_session(
        db,
        user_id=user.id,
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        access_expires_at=new_access_token_exp,
        refresh_expires_at=new_refresh_token_exp,
    )

    return new_access_token, new_refresh_token
