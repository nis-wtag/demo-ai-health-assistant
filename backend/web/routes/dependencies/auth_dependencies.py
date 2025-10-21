from functools import wraps

from core.database import DbSession
from fastapi import Cookie, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from services.dependencies.auth_dependencies import get_current_user
from sqlalchemy.orm import Session


async def require_login_for_template(
    db: DbSession,
    access_token: str = Cookie(None),
):
    try:
        return get_current_user(access_token=access_token, db=db)
    except HTTPException:
        return RedirectResponse(url="/login")
