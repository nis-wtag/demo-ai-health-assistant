from datetime import datetime, timezone

from core.database import DbSession
from fastapi import Depends, HTTPException, Request, status
from models.user import User, UserRole
from repositories.session_repository import SessionRepository
from repositories.user_repository import user_repository
from sqlalchemy.orm import Session


def get_current_user(request: Request, db: DbSession) -> User:
    if hasattr(request.state, "user") and request.state.user:
        return request.state.user

    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token missing"
        )

    session: Session = SessionRepository.get_by_access_token(db, access_token)
    if not session or not session.is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )
    if session.access_expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token expired"
        )

    user: User = user_repository.get_by_id(db, session.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


def require_roles(*roles: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return role_checker
