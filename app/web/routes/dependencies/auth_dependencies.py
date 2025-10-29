
from core.database import DbSession
from fastapi import Cookie, HTTPException
from fastapi.responses import RedirectResponse
from services.dependencies.auth_dependencies import get_current_user


async def require_login_for_template(
    db: DbSession,
    access_token: str = Cookie(None),
):
    try:
        return get_current_user(access_token=access_token, db=db)
    except HTTPException:
        return RedirectResponse(url="/login")
