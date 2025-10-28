from core.database import DbSession
from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
from services.dependencies.auth_dependencies import get_current_user


async def require_login_for_template(
    request: Request,
    db: DbSession,
):
    try:
        return get_current_user(request=request, db=db)
    except HTTPException:
        return RedirectResponse(url="/login")
