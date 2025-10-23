from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from web.routes.dependencies.auth_dependencies import require_login_for_template

router = APIRouter()
templates = Jinja2Templates(directory="web/templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, user=Depends(require_login_for_template)):
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "user": user}
    )
