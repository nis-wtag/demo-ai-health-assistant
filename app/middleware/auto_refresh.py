from datetime import datetime, timezone

from core.config import settings
from core.database import SessionLocal
from core.exceptions import UnauthorizedException
from fastapi import Request
from models import Session as SessionModel
from repositories.user_repository import user_repository
from services import session_service
from services.auth_service import refresh
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from middleware.logger import logger


class AutoRefreshMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        db: Session = SessionLocal()
        try:
            access_token = request.cookies.get("access_token")
            refresh_token = request.cookies.get("refresh_token")

            if access_token:
                try:
                    session: SessionModel = session_service.get_by_access_token(
                        db, access_token
                    )
                    if session and session.access_expires_at > datetime.now(
                        timezone.utc
                    ):
                        current_user = user_repository.get_by_id(db, session.user_id)
                        if current_user:
                            request.state.user = current_user
                            response = await call_next(request)
                            return response
                except Exception as e:
                    logger.error(f"Error validating access token: {e}", exc_info=True)

            if refresh_token:
                try:
                    session: SessionModel = session_service.get_by_refresh_token(
                        db, refresh_token
                    )
                    if session and session.refresh_expires_at > datetime.now(
                        timezone.utc
                    ):
                        current_user = user_repository.get_by_id(db, session.user_id)
                        if current_user:
                            request.state.user = current_user
                            response = await call_next(request)

                            # Attempt silent refresh
                            try:
                                new_access_token, new_refresh_token = refresh(
                                    db, refresh_token
                                )

                                # Update cookies
                                response.set_cookie(
                                    "access_token",
                                    new_access_token,
                                    httponly=settings.COOKIE_HTTPONLY,
                                    secure=settings.COOKIE_SECURE,
                                    samesite=settings.COOKIE_SAMESITE,
                                    max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
                                    * 60,
                                )
                                response.set_cookie(
                                    "refresh_token",
                                    new_refresh_token,
                                    httponly=settings.COOKIE_HTTPONLY,
                                    secure=settings.COOKIE_SECURE,
                                    samesite=settings.COOKIE_SAMESITE,
                                    max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
                                    * 24
                                    * 60
                                    * 60,
                                )
                            except Exception as e:
                                logger.error(
                                    f"Error refreshing tokens: {e}", exc_info=True
                                )
                                raise UnauthorizedException

                            return response
                except Exception as e:
                    logger.error(f"Error validating refresh token: {e}", exc_info=True)

            request.state.user = None
            return await call_next(request)

        except Exception as e:
            logger.exception(f"Middleware exception: {e}")
            request.state.user = None
            return await call_next(request)

        finally:
            db.close()
